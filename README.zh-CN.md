# site-kit

`jrtx.site` 产品家族所有站点的单一真源:一套设计系统、一个 i18n 引擎、一个下载解析器——让家族看起来是一个成熟的商业产品,而不是二十多个手搓页面。

[English](README.md)

## 为什么

过去每个家族站点各自手抄 CSS、i18n 词典和下载逻辑,结果是三套视觉方言、坏掉的语言切换、以及 Windows 访客拿到 macOS 安装包。本 kit 消灭所有副本:站点同步 kit 资产,CI 每周审计全族。

## 结构

```
dist/
  family.css   设计令牌 + 共享组件(导航、hero、卡片、页脚、双主题)
  family.js    主题 + i18n + 下载解析三合一引擎(零依赖)
  fonts/       自托管 Newsreader + Inter(禁 CDN、禁 Google Fonts)
template/
  index.html   范本页骨架,文档即示例
sync.sh        把 dist 资产同步进目标仓库的站点目录
check-site.py  按 kit 契约 lint 一个站点目录
family.json    全家族站点清单:仓库、URL、类型、有无安装包
.github/workflows/drift-check.yml  每周全族审计,漂移开 issue
```

## 用法

```sh
# 把某个站点仓库同步到当前 kit 版本
./sync.sh ~/Codes/fulcrum

# lint 某个站点目录
./check-site.py ~/Codes/fulcrum/site fulcrum
```

然后把站点 `index.html` 重排到模板骨架(导航 / hero / 特性 / 平台 / 上手 / 页脚),站点独有区块移入 `site.css`。

## 页面契约

- `<html data-kit-id="<site-id>">` — 决定每站存储键(`<site-id>-theme`、`<site-id>-lang-override-v2`)。
- 词典:`<script type="application/json" id="kit-i18n">`,zh 与 en 双词典必须完整;`data-i18n` 只放叶子元素。
- 下载:`<script type="application/json" id="kit-download">` 声明仓库与资产命名模式。解析器永远不给未知平台默认 macOS;解析不出就回落 Releases 页。
- 语言:手动选择优先,否则跟随浏览器语言;`languagechange` 实时生效。
- 字体与全部资产自托管。禁止引用 Google Fonts 与任何 CDN。

## 版本

`VERSION` 是 kit 版本。`sync.sh` 打版本戳;`check-site.py` 对过期戳报错;`drift-check.yml` 对线上漂移开 issue。

## 许可

[MIT](LICENSE)
