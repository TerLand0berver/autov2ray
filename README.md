## English

### Free Proxy to Clash Subscription Generator

This project automatically fetches free **socks5** and proxies from a public API, converts them into a Clash-compatible YAML subscription, and publishes it via GitHub Actions.

### Features
- Supports over 250 countries and regions.
- Fetches both **socks5** and proxies.
- Groups proxies by country, with a global selector.
- Skips countries with no proxies for 3 days to reduce invalid requests.
- Updates every minute via GitHub Actions.
- API URL is hidden via GitHub Secrets for security.

### Usage
1. **Set GitHub Secret**  
   - Add a secret named `PROXY_API_URL` with your API endpoint.

2. **Configure GitHub Actions**  
   - The workflow runs every minute automatically.
   - It generates `sub.yaml` and publishes it to the `gh-pages` branch.
   - Your subscription link:  
     `https://TerLand0berver.github.io/autov2ray/sub.yaml`

3. **Import into Clash**  
   - Use the above link as your Clash subscription URL.

### Notes
- The script skips countries with no proxies for 3 days.
- Supports both socks5 and http proxies.
- You can customize the country list and other parameters in the script.

---

## 简体中文

### 免费代理转Clash订阅生成器

本项目自动从公共API抓取免费的**socks5**和代理，转换为Clash兼容的YAML订阅，并通过GitHub Actions自动发布。

### 功能特点
- 支持全球250多个国家和地区。
- 同时获取**socks5**代理。
- 按国家分组，支持全局选择。
- 对无代理的国家自动跳过3天，减少无效请求。
- 每分钟自动更新订阅。
- API地址通过GitHub密钥隐藏，保障安全。

### 使用方法
1. **设置GitHub密钥**  
   - 在仓库Secrets中添加名为`PROXY_API_URL`的密钥，值为API地址。

2. **配置GitHub Actions**  
   - 工作流每分钟自动运行。  
   - 自动生成`sub.yaml`，发布到`gh-pages`分支。  
   - 订阅链接：  
     `https://TerLand0berver.github.io/autov2ray/sub.yaml`

3. **导入Clash**  
   - 使用上述链接作为Clash订阅地址。

### 注意事项
- 对无代理的国家自动跳过3天。
- 支持socks5两种代理。
- 可在脚本中自定义国家列表和参数。