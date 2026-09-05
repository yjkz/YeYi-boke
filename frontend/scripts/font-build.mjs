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

// 后处理：cn-font-split 生成的是 ./xxx.woff2 相对 URL，统一改写为站点绝对路径
const rawCss = fs.readFileSync(path.join(outDir, 'result.css'), 'utf8');
const fontCss = rawCss.replace(/url\("\.\/([^"]+\.woff2)"\)/g, `url("${cssUrlPrefix}/$1")`);
fs.writeFileSync(cssTarget, fontCss.trimEnd() + '\n');

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
