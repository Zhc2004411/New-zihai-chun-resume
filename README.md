# 小资的个人简历

项目包含两个版本：

- `docs/`：公网网站版本，可通过 GitHub Pages 发布，任何人用浏览器或扫码访问。
- `pages/`、`app.json` 等：微信小程序版本，可用微信开发者工具导入预览。

## 公网网站

发布目录：

```text
docs/
```

计划访问地址：

```text
https://zhc2004411.github.io/New-zihai-chun-resume/
```

二维码图片：

```text
docs/assets/site-qrcode.png
```

这个二维码已经按上面的公网地址生成。仓库发布到 GitHub Pages 后，扫码即可进入网站。

## GitHub Pages 发布方式

1. 在 GitHub 创建公开仓库：`zihai-chun-resume`
2. 将本项目推送到该仓库的 `main` 分支。
3. 进入仓库 `Settings` -> `Pages`。
4. `Build and deployment` 选择 `GitHub Actions`。
5. 等待 `Deploy resume website` 工作流完成。
6. 打开 `https://zhc2004411.github.io/New-zihai-chun-resume/` 验证网站。

项目已包含自动发布配置：

```text
.github/workflows/pages.yml
```

## 微信小程序预览

1. 打开微信开发者工具。
2. 选择“导入项目”。
3. 项目目录选择当前文件夹。
4. 使用当前 AppID 或测试号导入。
5. 点击“编译”即可预览。
