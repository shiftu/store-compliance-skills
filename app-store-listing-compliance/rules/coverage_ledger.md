# 覆盖台账

生成物：`python3 _tools/build_ledger.py`。口径见 `design/DESIGN.md` §12。
去向只有三种：**rule**（指向规则 id）/ **vision**（可做但未建规则）/ **human**（外部不可判 + 理由）。

Apple 130 个条号：rule 44 / vision 2 / human 84；Play 114 个领域：rule 58 / human 56；未分类 0；无条号归属的规则 0。

## Apple

| 条号 | 标题 | 去向 | 规则 / 理由 |
|---|---|---|---|
| 1.1 | Objectionable Content | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.2 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.3 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.4 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.5 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.6 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.1.7 |  | human | 内容禁止项：需应用内实际内容判定，商店页只见描述 |
| 1.2 | User-Generated Content | rule | ASRG-1.2-UGC、ASRG-1.2-RANDOM-CHAT |
| 1.2.1 | Creator Content | rule | ASRG-1.2.1a-AGE-GATE |
| 1.3 | Kids Category | rule | ASRG-1.3-KIDS |
| 1.4 | Physical Harm | human | 人身伤害相关内容：需产品实际功能判定 |
| 1.4.1 |  | rule | ASRG-1.4.1-MEDICAL |
| 1.4.2 |  | human | 人身伤害相关内容：需产品实际功能判定 |
| 1.4.3 |  | human | 人身伤害相关内容：需产品实际功能判定 |
| 1.4.4 |  | human | 人身伤害相关内容：需产品实际功能判定 |
| 1.4.5 |  | human | 人身伤害相关内容：需产品实际功能判定 |
| 1.5 | Developer Information | rule | ASRG-1.5-SUPPORT |
| 1.6 | Data Security | human | 数据安全实现：需安装包或渗透测试 |
| 1.7 | Reporting Criminal Activity | human | 犯罪活动举报流程：需联系与响应记录 |
| 2.1 | App Completeness | rule | ASRG-2.1-COMPLETE |
| 2.2 | Beta Testing | human | Beta 测试：TestFlight 与内部轨道外部不可见 |
| 2.3 | Accurate Metadata | human | 元数据/功能：条款不落在商店页可见面 |
| 2.3.1 |  | rule | ASRG-2.1-COMPLETE |
| 2.3.2 |  | rule | ASRG-2.3.2-IAP-DISCLOSURE |
| 2.3.3 |  | rule | ASRG-2.3.3-SCREENSHOTS |
| 2.3.4 |  | vision | 预览视频内容，需下载视频判读；尚未建规则 |
| 2.3.5 |  | vision | 截图选取与顺序（是否误导），需看图；尚未建规则 |
| 2.3.6 |  | rule | ASRG-2.3.6-AGE-RATING、ASRG-AGE-RATING-FORM |
| 2.3.7 |  | rule | ASRG-2.3.7-NAME |
| 2.3.8 |  | rule | ASRG-2.3.8-META-4PLUS |
| 2.3.9 |  | human | 元数据细节：需图片/更新说明/权利材料 |
| 2.3.10 |  | rule | ASRG-2.3.10-OTHERPLATFORMS |
| 2.3.11 |  | human | 元数据细节：需图片/更新说明/权利材料 |
| 2.3.12 |  | human | 元数据细节：需图片/更新说明/权利材料 |
| 2.3.13 |  | human | 元数据细节：需图片/更新说明/权利材料 |
| 2.3.14 |  | rule | ASRG-2.3.14-ASSETS |
| 2.4 | Hardware Compatibility | human | 硬件兼容：需真机 |
| 2.4.1 |  | human | 硬件兼容：需真机 |
| 2.4.2 |  | human | 硬件兼容：需真机 |
| 2.4.3 |  | human | 硬件兼容：需真机 |
| 2.4.4 |  | human | 硬件兼容：需真机 |
| 2.4.5 |  | human | 硬件兼容：需真机 |
| 2.5 | Software Requirements | human | 软件要求：需安装包与审核备注 |
| 2.5.1 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.2 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.3 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.4 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.5 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.6 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.7 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.8 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.9 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.10 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.11 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.12 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.13 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.14 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.15 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.16 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.17 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.18 |  | human | 软件要求：需安装包与审核备注 |
| 2.5.19 |  | rule | ASRG-2.5.19-HIDDEN |
| 3.1 | Payments | human | 业务条款：需后台/合同/地区配置 |
| 3.1.1 | In-App Purchase: | rule | ASRG-3.1.1-IAP |
| 3.1.2 | Subscriptions: | rule | ASRG-3.1.2c-SUBINFO、ASRG-SUB-CHECKLIST、ASRG-3.1.2a-ONGOING、ASRG-3.1.2-SCAM |
| 3.1.3 | Other Purchase Methods: | human | 其他购买方式/加密/内容访问：需安装包与地区配置 |
| 3.1.4 | Hardware-Specific Content: | human | 其他购买方式/加密/内容访问：需安装包与地区配置 |
| 3.1.5 | Cryptocurrencies: | human | 其他购买方式/加密/内容访问：需安装包与地区配置 |
| 3.2 | Other Business Model Issues | human | 其他业务模式：需后台与合同 |
| 3.2.1 | Acceptable | human | 其他业务模式：需后台与合同 |
| 3.2.2 | Unacceptable | rule | ASRG-3.2.2x-FORCE-RATE |
| 4.1 | Copycats | human | 抄袭复制：需与在先作品比对，人工判断 |
| 4.2 | Minimum Functionality | rule | ASRG-4.2-MINFUNC |
| 4.2.1 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.2 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.3 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.4 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.5 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.6 |  | rule | ASRG-4.2-MINFUNC |
| 4.2.7 | Remote Desktop Clients: | rule | ASRG-4.2-MINFUNC |
| 4.3 | Spam | rule | ASRG-4.3-FORTUNE、ASRG-4.3b-SATURATED、ASRG-4.3-MULTI-BUNDLE |
| 4.4 | Extensions | human | 扩展与插件：需安装包 |
| 4.4.1 |  | human | 扩展与插件：需安装包 |
| 4.4.2 |  | human | 扩展与插件：需安装包 |
| 4.4.3 |  | human | 扩展与插件：需安装包 |
| 4.5 | Apple Sites and Services | human | Apple 站点与服务使用：需行为记录 |
| 4.5.1 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.5.2 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.5.3 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.5.4 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.5.5 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.5.6 |  | human | Apple 站点与服务使用：需行为记录 |
| 4.6 |  | human | 替代分发市场：需资质材料 |
| 4.7 | Mini apps, mini games, streaming games, chatbots, plug-ins, and game emulators | rule | ASRG-4.7-CHATBOT |
| 4.7.1 |  | rule | ASRG-4.7-CHATBOT |
| 4.7.2 |  | rule | ASRG-4.7-CHATBOT |
| 4.7.3 |  | rule | ASRG-4.7-CHATBOT |
| 4.7.4 |  | rule | ASRG-4.7-CHATBOT |
| 4.7.5 |  | rule | ASRG-4.7.5-AGE |
| 4.8 | Login Services | rule | ASRG-4.8-LOGIN |
| 4.9 | Apple Pay | human | Apple Pay：需支付集成与商户配置 |
| 4.10 | Monetizing Built-In Capabilities | human | 抄袭复制：需与在先作品比对，人工判断 |
| 5.1 | Privacy | human | 法律与隐私条款：需合同或人工判断 |
| 5.1.1 | Data Collection and Storage | rule | ASRG-5.1.1i-PRIVACY、ASRG-5.1.1v-ACCOUNT-DELETE、ASRG-PRIVACY-LABEL |
| 5.1.2 | Data Use and Sharing | rule | ASRG-5.1.2i-AI-SHARING、ASRG-5.1.2ii-PURPOSE |
| 5.1.3 | Health and Health Research | rule | ASRG-5.1.3-HEALTH |
| 5.1.4 | Kids | rule | ASRG-5.1.4-KIDS-DATA |
| 5.1.5 | Location Services | human | 位置数据：需安装包与系统权限弹窗 |
| 5.2 | Intellectual Property | human | 知识产权：需权利材料与人工判断 |
| 5.2.1 | Generally: | human | 知识产权：需权利材料与人工判断 |
| 5.2.2 | Third-Party Sites/Services: | human | 知识产权：需权利材料与人工判断 |
| 5.2.3 | Audio/Video Downloading: | human | 知识产权：需权利材料与人工判断 |
| 5.2.4 | Apple Endorsements: | human | 知识产权：需权利材料与人工判断 |
| 5.2.5 | Apple Products: | human | 知识产权：需权利材料与人工判断 |
| 5.3 | Gaming, Gambling, and Lotteries | rule | ASRG-5.3.4-GAMBLING |
| 5.3.1 |  | human | 法律与隐私条款：需合同或人工判断 |
| 5.3.2 |  | human | 法律与隐私条款：需合同或人工判断 |
| 5.3.3 |  | human | 法律与隐私条款：需合同或人工判断 |
| 5.3.4 |  | human | 法律与隐私条款：需合同或人工判断 |
| 5.4 | VPN Apps | human | VPN 应用：需技术与资质 |
| 5.5 | Mobile Device Management | human | 移动设备管理：需企业资质 |
| 5.6 | Developer Code of Conduct | human | 法律与隐私条款：需合同或人工判断 |
| 5.6.1 | App Store Reviews | human | 开发者行为准则/发现欺诈：需行为证据 |
| 5.6.2 | Developer Identity | rule | ASRG-5.6.2-DEV-IDENTITY |
| 5.6.3 | Discovery Fraud | human | 开发者行为准则/发现欺诈：需行为证据 |
| 5.6.4 | App Quality | human | 法律与隐私条款：需合同或人工判断 |
| 年龄分级问卷 | App Store Connect 年龄分级（2026-11 新增 Dating / Shared Location 项） | rule | ASRG-2.3.6-AGE-RATING、ASRG-AGE-RATING-FORM、ASRG-AGE-DATING-COMPANION、ASRG-AGE-SHARED-LOCATION |
| EU DSA 交易者 | DSA 交易者身份与联系方式披露（ASC 合规信息） | rule | ASRG-DSA-TRADER |
| DPLA Schedule 2 | 开发者协议附则 2（订阅/内购披露义务归属） | rule | ASRG-DPLA-S2-3.2 |
| 1.1.1 | （并入 1.1 内容禁止项） | rule | ASRG-1.2-PORN |

## Google Play

| 领域 | 标题 | 去向 | 规则 / 理由 |
|---|---|---|---|
| Child Endangerment |  | rule | GP-FAM-01-FAMILIES |
| Inappropriate Content |  | rule | GP-META-03-SUGGESTIVE、GP-AGE-01-BLOCK-MINORS |
| Sexual Content and Profanity |  | rule | GP-META-03-SUGGESTIVE |
| Hate Speech |  | human | 内容判断：需看应用内 UGC 与审核记录 |
| Violence |  | human | 内容判断：需应用内实际内容 |
| Violent Extremism |  | human | 内容判断：需应用内实际内容 |
| Sensitive Events |  | human | 内容判断：需应用内实际内容 |
| Bullying and Harassment |  | human | 内容判断：需应用内实际内容 |
| Dangerous Products |  | human | 商品/内容判定：需看交易与展示 |
| Marijuana |  | human | 商品/内容判定：需看交易与展示 |
| Tobacco and Alcohol |  | human | 商品/内容判定：需看交易与展示 |
| Age-Restricted Content and Functionality |  | rule | GP-AGE-01-BLOCK-MINORS |
| Financial Services |  | human | 金融资质：需牌照与地区材料 |
| Binary Options |  | human | 金融资质：需牌照与地区材料 |
| Loans |  | human | 金融资质：需牌照与地区材料 |
| Earned Wage Access |  | human | 金融资质：需牌照与地区材料 |
| Country specific requirements |  | human | 金融资质：需牌照与地区材料 |
| Real-Money Gambling, Games, and Contests |  | human | 博彩资质：需牌照与地区配置 |
| Illegal Activities |  | human | 违法活动：需内容与行为证据 |
| User Generated Content |  | rule | GP-UGC-01-MODERATION |
| Health Content and Services |  | rule | GP-HEALTH-01-CLAIMS、GP-HEALTH-02-DISCLAIMER |
| Health and Medical Apps |  | rule | GP-HEALTH-01-CLAIMS、GP-HEALTH-02-DISCLAIMER |
| Health Connect Data |  | human | 健康细分：需功能与资质材料 |
| Prescription Drugs |  | human | 健康细分：需功能与资质材料 |
| Unapproved Substances |  | human | 健康细分：需功能与资质材料 |
| Health Misinformation |  | human | 健康细分：需功能与资质材料 |
| Payments - Clinical Services |  | rule | GP-PAY-01-BILLING |
| Blockchain-based Content |  | human | 加密资产：需地区配置与牌照 |
| AI-Generated Content |  | rule | GP-AI-01-REPORT、GP-AI-02-RESTRICTED |
| Intellectual Property |  | human | IP 侵权：需权利材料与人工比对 |
| Privacy, Deception and Device Abuse |  | human | 技术实现：需安装包 |
| User Data |  | rule | GP-UD-01-PRIVACY、GP-UD-05-ACCOUNT-DELETE |
| Personal and Sensitive User Data |  | rule | GP-UD-03-PROMINENT、GP-UD-06-PERSISTENT-ID |
| Prominent Disclosure & Consent Requirement |  | rule | GP-UD-03-PROMINENT、GP-UD-06-PERSISTENT-ID |
| Restrictions for Personal and Sensitive Data Access |  | rule | GP-UD-03-PROMINENT、GP-UD-06-PERSISTENT-ID |
| Data safety section |  | rule | GP-UD-02-DATA-SAFETY |
| Privacy Policy |  | rule | GP-UD-01-PRIVACY |
| Account Deletion Requirement |  | rule | GP-DEV-01-VERIFY |
| Usage of App Set ID |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| EU-U.S., UK, and Swiss Data Privacy Frameworks |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Permissions and APIs that Access Sensitive Information |  | human | 技术实现：需安装包 |
| Restricted Permissions |  | rule | GP-SENS-01-LOCATION |
| Restricted Permissions with minimum scope alternatives |  | rule | GP-SENS-01-LOCATION |
| SMS and Call Log Permissions |  | human | 技术实现：需安装包 |
| Location Permissions |  | rule | GP-SENS-01-LOCATION |
| Package (App) Visibility Permission |  | rule | GP-PKG-01-REGISTER |
| Accessibility API |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Request Install Packages Permission |  | rule | GP-PKG-01-REGISTER |
| Body Sensor Permissions |  | human | 技术实现：需安装包 |
| Health Connect by Android Permissions |  | human | 健康细分：需功能与资质材料 |
| VPN Service |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Exact Alarm Permission |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Full-Screen Intent Permission |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Age Signals API and User Data |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Device and Network Abuse |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Permissions for Foreground Services (FGS) |  | human | 技术实现：需安装包 |
| User-Initiated Data Transfer Jobs |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Flag Secure Requirements |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Apps that Run On-device Android Containers |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Deceptive Behavior |  | rule | GP-DEC-01-METADATA、GP-DEC-02-REVIEW |
| 1. Misleading Claims |  | rule | GP-DEC-01-METADATA |
| 2. Deceptive Device Settings Changes |  | rule | GP-DEC-01-METADATA |
| 3. Enabling Dishonest Behavior |  | rule | GP-DEC-01-METADATA |
| 4. Manipulated Media |  | rule | GP-DEC-01-METADATA |
| 5. Behavior Transparency |  | rule | GP-DEC-01-METADATA |
| Misrepresentation |  | rule | GP-MIS-01-IMPERSONATION |
| Google Play's Target API Level Policy |  | human | API / 权限 / 合规框架的声明型要求：需 Play Console 申报或安装包 |
| Use of SDKs In Apps |  | rule | GP-UD-04-THIRD-PARTY-AI |
| SDK Requirements |  | rule | GP-UD-04-THIRD-PARTY-AI |
| Malware |  | human | 技术实现：需安装包 |
| Backdoors |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Billing Fraud |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Stalkerware |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Denial of Service (DoS) |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Hostile Downloaders |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Non-Android Threat |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Phishing |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Elevated Privilege Abuse |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Ransomware |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Rooting |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Spam |  | rule | GP-SPAM-01-REPETITIVE、GP-SPAM-02-WEBVIEW |
| Spyware |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Trojan |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Riskware |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Impersonation |  | rule | GP-MIS-01-IMPERSONATION |
| Mobile Unwanted Software |  | human | 恶意软件/滥用分类：需安装包分析（人工或沙箱） |
| Ad Fraud |  | rule | GP-ADS-01-DECEPTIVE |
| Unauthorized Use or Imitation of System Functionality |  | rule | GP-FUNC-01-BROKEN |
| Social Engineering |  | rule | GP-DEC-01-METADATA |
| Monetization and Ads |  | rule | GP-ADS-01-DECEPTIVE、GP-ADS-02-INTERSTITIAL |
| Payments |  | rule | GP-PAY-01-BILLING |
| Ads |  | rule | GP-ADS-01-DECEPTIVE、GP-ADS-02-INTERSTITIAL |
| Subscriptions |  | rule | GP-SUB-01-DISCLOSURE、GP-SUB-02-VALUE、GP-SUB-03-TRIAL、GP-SUB-04-LOCALIZED、GP-SUB-05-ELIGIBILITY |
| Families Self-Certified Ads SDK Program |  | rule | GP-FAM-01-FAMILIES、GP-FAM-02-AGE-SCREEN |
| Store Listing and Promotion |  | rule | GP-META-01-TITLE、GP-META-02-DESCRIPTION |
| App Promotion |  | rule | GP-ADS-01-DECEPTIVE |
| Metadata |  | rule | GP-META-01-TITLE、GP-META-02-DESCRIPTION |
| User Ratings, Reviews, and Installs |  | rule | GP-RATE-01-IARC |
| Content Ratings |  | rule | GP-RATE-01-IARC |
| Spam, Functionality, and User Experience |  | rule | GP-SPAM-01-REPETITIVE、GP-SPAM-02-WEBVIEW |
| Functionality, Content, and User Experience |  | rule | GP-FUNC-01-BROKEN |
| 1. Limited Functionality and Content |  | rule | GP-FUNC-01-BROKEN |
| 2. Broken Functionality |  | rule | GP-FUNC-01-BROKEN |
| Android Instant Apps |  | human | 细分投放形态政策：当前品类不涉及 |
| Android Emoji Policy |  | human | 细分投放形态政策：当前品类不涉及 |
| Families |  | rule | GP-FAM-01-FAMILIES、GP-FAM-02-AGE-SCREEN |
| Google Play Families Policies |  | rule | GP-FAM-01-FAMILIES、GP-FAM-02-AGE-SCREEN |
| Families Policy Requirements |  | rule | GP-FAM-01-FAMILIES、GP-FAM-02-AGE-SCREEN |
| Ads and Monetization |  | rule | GP-ADS-01-DECEPTIVE、GP-ADS-02-INTERSTITIAL |
| Families Self-Certified Ads SDK Policy |  | rule | GP-FAM-01-FAMILIES、GP-FAM-02-AGE-SCREEN |
| Enforcement |  | rule | GP-ENF-01-RELATED |
| Enforcement Process |  | rule | GP-ENF-01-RELATED |
| Account Transfers |  | rule | GP-DEV-01-VERIFY |
| Trader status | EEA/UK 交易者声明（帮助中心独立政策） | rule | GP-TRADER-01-DSA |

