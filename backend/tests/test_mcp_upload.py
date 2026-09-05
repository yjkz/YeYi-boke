"""U1-U4 修复的回归测试：MCP base64 宽容解析、扩展名白名单、admin 上传一致性。"""

import base64
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.config import settings
from app.dependencies import require_admin
from app.main import app
from app.mcp.server import upload_image

CONTENT = b"\x89PNG\r\n\x1a\nfake-image-payload"


@pytest.fixture
def upload_dir(tmp_path, monkeypatch) -> Path:
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


def stored_file(upload_dir: Path) -> Path:
    files = list(upload_dir.iterdir())
    assert len(files) == 1
    return files[0]


def assert_upload_ok(result, upload_dir: Path, ext: str = ".png") -> None:
    assert result.size == len(CONTENT)
    assert result.url.startswith("/uploads/")
    assert result.url.endswith(ext)
    stored = stored_file(upload_dir)
    assert stored.name == result.url.removeprefix("/uploads/")
    assert stored.name.endswith(ext)
    assert stored.read_bytes() == CONTENT


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_accepts_newline_wrapped_base64(upload_dir):
    # 76 列 MIME 换行（`base64` 命令与剪贴板的标准输出）
    result = await upload_image("newline.png", base64.encodebytes(CONTENT).decode())
    assert_upload_ok(result, upload_dir)


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_accepts_data_uri(upload_dir):
    payload = "data:image/png;base64," + base64.b64encode(CONTENT).decode()
    result = await upload_image("data-uri.png", payload)
    assert_upload_ok(result, upload_dir)


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_accepts_urlsafe_base64(upload_dir):
    data = bytes([0xFB, 0xEF, 0xBE, 0xFF])  # 标准字母表里必然出现 '+' 和 '/'
    payload = base64.urlsafe_b64encode(data).decode()  # 对应 '-' 和 '_'
    assert "-" in payload and "_" in payload
    result = await upload_image("urlsafe.png", payload)
    assert result.size == len(data)
    assert stored_file(upload_dir).read_bytes() == data


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_accepts_missing_padding(upload_dir):
    payload = base64.b64encode(CONTENT).decode().rstrip("=")
    assert len(payload) % 4 in (2, 3)
    result = await upload_image("unpadded.png", payload)
    assert_upload_ok(result, upload_dir)


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_still_rejects_truly_invalid_base64(upload_dir):
    for payload in ("not-base64!", "====", "QUJDR"):  # 非法字符 / 纯 padding / 长度 %4==1
        with pytest.raises(ValueError, match="invalid"):
            await upload_image("ok.png", payload)
    assert list(upload_dir.iterdir()) == []


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_upload_rejects_oversized_payload_and_reports_limit(upload_dir, monkeypatch):
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE", 16)
    raw = base64.b64encode(b"x" * 32).decode()
    with pytest.raises(ValueError, match="exceeds the 16 byte upload limit"):
        await upload_image("big.png", raw)
    # 预检在规范化之后：夹带换行的超限 payload 同样按净长度拒绝
    wrapped = base64.encodebytes(b"x" * 32).decode()
    with pytest.raises(ValueError, match="exceeds the 16 byte upload limit"):
        await upload_image("big.png", wrapped)
    # 解码后恰好等于上限：允许
    boundary = await upload_image("boundary.png", base64.b64encode(b"y" * 16).decode())
    assert boundary.size == 16


@pytest.mark.no_db
@pytest.mark.asyncio
@pytest.mark.parametrize("filename", ["probe-x.html", "probe-x.svg", "probe-x.php", "no-ext"])
async def test_upload_rejects_non_image_extensions(upload_dir, filename):
    with pytest.raises(ValueError, match="unsupported image type"):
        await upload_image(filename, base64.b64encode(CONTENT).decode())
    assert list(upload_dir.iterdir()) == []


@pytest.mark.no_db
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filename,ext",
    [("a.PNG", ".png"), ("b.jpg", ".jpg"), ("c.JPEG", ".jpeg"), ("d.gif", ".gif"), ("e.webp", ".webp"), ("f.ico", ".ico")],
)
async def test_upload_allows_whitelisted_extensions(upload_dir, filename, ext):
    result = await upload_image(filename, base64.b64encode(CONTENT).decode())
    assert result.url.endswith(ext)
    assert stored_file(upload_dir).name.endswith(ext)
    assert stored_file(upload_dir).read_bytes() == CONTENT


@pytest.mark.no_db
@pytest.mark.asyncio
async def test_admin_upload_route_rejects_html_and_accepts_png(client, upload_dir):
    """admin REST /admin/upload 与 MCP 共用 upload_image_bytes，行为必须一致。"""

    async def fake_admin():
        return MagicMock(role="admin")

    app.dependency_overrides[require_admin] = fake_admin
    try:
        rejected = await client.post(
            "/api/v1/admin/upload",
            files={"file": ("evil.html", b"<script>alert(1)</script>", "text/html")},
        )
        assert rejected.status_code == 400
        assert "unsupported image type" in rejected.json()["detail"]

        accepted = await client.post(
            "/api/v1/admin/upload",
            files={"file": ("ok.png", CONTENT, "image/png")},
        )
        assert accepted.status_code == 200
        url = accepted.json()["url"]
        assert url.startswith("/uploads/") and url.endswith(".png")
        assert stored_file(upload_dir).read_bytes() == CONTENT
    finally:
        app.dependency_overrides.pop(require_admin, None)
