// 构建时字体子集化：阿里妈妈方圆体 OTF → woff2 分片 + unicode-range 按需加载 CSS
// 产物：
//   public/fonts/fangyuan/*.woff2  —— 内容哈希命名的分片（构建时生成，不入 git）
//   assets/css/font-split.css      —— @font-face + unicode-range，URL 已改为站点绝对路径
// font-family 保持 "Alimama FangYuanTi"，与旧 @font-face 的 font-style/weight/display 一致。
import { fontSplit } from 'cn-font-split';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const input = path.join(appRoot, 'assets', 'fonts', 'AlimamaFangYuanTi.otf');
const outDir = path.join(appRoot, 'public', 'fonts', 'fangyuan');
const cssTarget = path.join(appRoot, 'assets', 'css', 'font-split.css');
const cssUrlPrefix = '/fonts/fangyuan';

// 清理旧分片，避免哈希名变更后残留孤儿文件
fs.rmSync(outDir, { recursive: true, force: true });

await fontSplit({
  input,
  outDir,
  targetType: 'woff2',
  css: {
    fontFamily: 'Alimama FangYuanTi',
    fontWeight: '400',
    fontStyle: 'normal',
    fontDisplay: 'swap',
  },
  reporter: false,
  testHtml: false,
});

// 后处理：cn-font-split 生成的是 ./xxx.woff2 相对 URL，统一改写为站点绝对路径。
// 兼容单双引号写法，防止上游升级改变输出格式后改写静默失效（会导致运行时字体 404）
const rawCss = fs.readFileSync(path.join(outDir, 'result.css'), 'utf8');
const fontFaceCount = (rawCss.match(/@font-face\b/g) || []).length;
let rewriteCount = 0;
const fontCss = rawCss.replace(
  /url\((['"])\.\/([^'"]+\.woff2)\1\)/g,
  (_match, _quote, file) => {
    rewriteCount += 1;
    return `url("${cssUrlPrefix}/${file}")`;
  },
);
fs.writeFileSync(cssTarget, fontCss.trimEnd() + '\n');

// 断言：改写必须 100% 覆盖 —— 残留相对路径或漏改的 @font-face 都意味着运行时字体 404
if (fontFaceCount === 0) {
  throw new Error('[font:build] result.css 中没有 @font-face 块，cn-font-split 输出格式可能已变化');
}
const leftoverRelativeUrls = (fontCss.match(/url\((['"])\.\//g) || []).length;
if (rewriteCount !== fontFaceCount || leftoverRelativeUrls !== 0) {
  throw new Error(
    `[font:build] URL 改写不完整：@font-face ${fontFaceCount} 块，仅改写 ${rewriteCount} 处，` +
      `残留相对路径 ${leftoverRelativeUrls} 处，请检查 cn-font-split 输出格式`,
  );
}

// 分片目录只保留 woff2，中间产物不进公开产物
fs.rmSync(path.join(outDir, 'result.css'), { force: true });
fs.rmSync(path.join(outDir, 'index.proto'), { force: true });

const chunks = fs.readdirSync(outDir).filter((f) => f.endsWith('.woff2'));
const sizes = chunks.map((f) => fs.statSync(path.join(outDir, f)).size);
const total = sizes.reduce((a, b) => a + b, 0);
const max = sizes.length ? Math.max(...sizes) : 0;
console.log(
  `[font:build] ${chunks.length} woff2 chunks -> ${path.relative(appRoot, outDir)}`,
);
console.log(
  `[font:build] total ${(total / 1024 / 1024).toFixed(2)} MB, largest chunk ${(max / 1024).toFixed(1)} KB`,
);
console.log(`[font:build] css -> ${path.relative(appRoot, cssTarget)}`);

// cn-font-split 的原生内核（koffi FFI）在脚本工作全部完成后残留存活句柄，导致 Node 进程不退出
// （Windows 上表现为退出时段错误，Linux 容器内表现为 RUN 挂死）。
// 本脚本此前的所有写入均为同步 fs 且断言失败会先行 throw，走到这里即代表全部成功，强制退出安全。
process.exit(0);
