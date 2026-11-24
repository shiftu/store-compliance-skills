# 商店政策原文索引（阶段 1）

抓取工具：`curl` + `bs4`/`markdownify` 本地转写（`_tools/html2md.py`），少量页面用 `tinyfish fetch content get`
（`_tools/fetch_src.py`）。之所以不全用 tinyfish：它对 Apple 指南页的 markdown 抽取会丢掉整个第 2 节和
3.x 全部子条款（实测 76k 字符 vs 实际 100k），本地转写保留服务端渲染的完整 HTML。

- 抓取日期：2026-11-23（本地时区 UTC-6，对应简报当日）
- 留痕：`_logs/fetch_2026-11-23.jsonl`，共 **57** 行；本索引里每个 URL 都能在该日志中找到 `status=ok` 的记录
- 每条日志字段：`ts` / `tool` / `query_or_url` / `status`(ok|blocked|empty) / `used_for`

## Apple

| 文件 | URL | 抓取时间 | 字符 | 覆盖条款 | 完整性 |
| --- | --- | --- | --- | --- | --- |
| [`apple/age_rating.md`](apple/age_rating.md) | https://developer.apple.com/help/app-store-connect/manage-app-information/set-an-app-age-rating/ | 2026-11-23T23:57:59-06:00 | 8962 | App Store Connect 年龄分级问卷操作与新分级体系 | 完整 |
| [`apple/age_rating_values.md`](apple/age_rating_values.md) | https://developer.apple.com/help/app-store-connect/reference/app-information/age-ratings-values-and-definitions | 2026-11-24T00:02:34-06:00 | 28616 | 年龄分级取值与定义（4+/9+/13+/16+/18+ 及分区取值） | 完整 |
| [`apple/app_privacy_details.md`](apple/app_privacy_details.md) | https://developer.apple.com/app-store/app-privacy-details/ | 2026-11-23T23:58:05-06:00 | 20623 | App 隐私标签（App Privacy Details）数据类型与用途填写规范 | 完整 |
| [`apple/dpla.md`](apple/dpla.md) | https://developer.apple.com/support/terms/apple-developer-program-license-agreement/ | 2026-11-24T00:03:54-06:00 | 628473 | Developer Program License Agreement 全文（Schedule 1/2/3；2.3 / 2.6 / 3.2 订阅与内购披露条款） | 完整（HTML 正文转写，628k 字符） |
| [`apple/dsa_trader.md`](apple/dsa_trader.md) | https://developer.apple.com/help/app-store-connect/manage-compliance-information/manage-european-union-digital-services-act-trader-requirements/ | 2026-11-23T23:58:03-06:00 | 8340 | EU DSA 第 30/31 条：交易者身份核验与商店页展示（地址/电话/邮箱） | 完整 |
| [`apple/guidelines.md`](apple/guidelines.md) | https://developer.apple.com/app-store/review/guidelines/ | 2026-11-23T23:57:01-06:00 | 100038 | App Review Guidelines 全文：Introduction / Before You Submit / 1 Safety / 2 Performance / 3 Business / 4 Design / 5 Legal / After You Submit | 完整；Last Updated: October 16, 2026 |
| [`apple/news_guidelines_2026-04-XX.md`](apple/news_guidelines_2026-04-XX.md) | https://developer.apple.com/news/?id=ey6d8onl | 2026-11-24T00:02:53-06:00 | 1959 | 指南改版公告：1.2.1(a) 创作者内容年龄限制机制、2.5.10 等 | 完整（标题日期以正文为准） |
| [`apple/news_guidelines_2026-10-16.md`](apple/news_guidelines_2026-10-16.md) | https://developer.apple.com/news/?id=92th7e5i | 2026-11-23T23:57:46-06:00 | 1382 | 指南 2026-10-16 改版公告：逐条列出改动（1.2、2.3.1、4.7、5.1.2 等） | 完整 |
| [`apple/news_guidelines_chat_ugc.md`](apple/news_guidelines_chat_ugc.md) | https://developer.apple.com/news/?id=d75yllv4 | 2026-11-24T00:02:55-06:00 | 464 | 指南澄清：随机/匿名聊天纳入 1.2 用户生成内容 | 完整（短公告） |
| [`apple/news_nonconsensual_nudity.md`](apple/news_nonconsensual_nudity.md) | https://developer.apple.com/news/?id=vvzx6cul | 2026-11-24T00:02:58-06:00 | 3585 | 指南强化：非自愿私密影像与 AI 生成裸露内容 | 完整 |
| [`apple/subscriptions.md`](apple/subscriptions.md) | https://developer.apple.com/app-store/subscriptions/ | 2026-11-23T23:58:08-06:00 | 45707 | 自动续期订阅：订阅信息、优惠、试用、升降级、商店页披露 | 完整 |
| [`apple/upcoming_requirements.md`](apple/upcoming_requirements.md) | https://developer.apple.com/news/upcoming-requirements/ | 2026-11-24T00:03:01-06:00 | 9489 | 即将生效要求清单（年龄分级问卷 2026-01-31 截止、DSA 等） | 完整 |

## Google Play

| 文件 | URL | 抓取时间 | 字符 | 覆盖条款 | 完整性 |
| --- | --- | --- | --- | --- | --- |
| [`play/ads.md`](play/ads.md) | https://support.google.com/googleplay/android-developer/answer/9857753 | 2026-11-24T00:00:10-06:00 | 12573 | Ads 政策（欺骗性广告、插屏、广告与内容区分） | 完整 |
| [`play/age_restricted.md`](play/age_restricted.md) | https://support.google.com/googleplay/android-developer/answer/16302250 | 2026-11-23T23:59:50-06:00 | 1136 | Age-Restricted Content and Functionality（赌博/约会/随机连麦/匿名聊天须屏蔽未成年人） | 完整（短条款全文） |
| [`play/age_signals.md`](play/age_signals.md) | https://developer.android.com/google/play/age-signals/use-age-signals-api | 2026-11-24T00:04:46-06:00 | 1886 | Play Age Signals API（年龄保证/家庭体验） | 完整 |
| [`play/ai_generated.md`](play/ai_generated.md) | https://support.google.com/googleplay/android-developer/answer/13985936 | 2026-11-23T23:58:40-06:00 | 1918 | AI 生成内容政策（禁止生成受限内容、必须有应用内举报/标记功能） | 完整（短条款全文） |
| [`play/android_developer_verification.md`](play/android_developer_verification.md) | https://developer.android.com/developer-verification | 2026-11-24T00:02:30-06:00 | 4005 | Android developer verification 官方说明 | 完整 |
| [`play/announcement_2026-04-15.md`](play/announcement_2026-04-15.md) | https://support.google.com/googleplay/android-developer/answer/16926792 | 2026-11-24T00:01:53-06:00 | 5252 | 政策公告 2026-04-15 | 完整 |
| [`play/announcement_2026-07-15.md`](play/announcement_2026-07-15.md) | https://support.google.com/googleplay/android-developer/answer/17134731 | 2026-11-24T00:01:59-06:00 | 6161 | 政策公告 2026-07-15（target API、开发者验证等） | 完整 |
| [`play/announcement_2026-10-29.md`](play/announcement_2026-10-29.md) | https://support.google.com/googleplay/android-developer/answer/18100766 | 2026-11-24T00:01:47-06:00 | 7899 | 政策公告 2026-10-29：新政策（本地网络/联系人权限/AppFunctions）、订阅资格折扣、Payments 澄清、Play Age Signals、trader 声明 | 完整 |
| [`play/appeals.md`](play/appeals.md) | https://support.google.com/googleplay/android-developer/answer/9899142 | 2026-11-24T00:00:20-06:00 | 2092 | Managing Policy Violations and Appeals | 完整 |
| [`play/child_endangerment.md`](play/child_endangerment.md) | https://support.google.com/googleplay/android-developer/answer/9878809 | 2026-11-24T00:00:36-06:00 | 5548 | Child Endangerment 政策 | 完整 |
| [`play/content_ratings.md`](play/content_ratings.md) | https://support.google.com/googleplay/android-developer/answer/9898843 | 2026-11-23T23:59:21-06:00 | 3889 | Content Ratings（IARC 问卷、分级不实） | 完整 |
| [`play/data_safety.md`](play/data_safety.md) | https://support.google.com/googleplay/android-developer/answer/10787469 | 2026-11-23T23:58:20-06:00 | 70330 | Data safety 表单（数据类别、用途、共享、安全实践、各问题 ID 与答案要求） | 完整（含问题清单表） |
| [`play/deceptive_behavior.md`](play/deceptive_behavior.md) | https://support.google.com/googleplay/android-developer/answer/9888077 | 2026-11-23T23:58:51-06:00 | 15616 | Deceptive Behavior 政策（虚假功能、误导性声明、操纵审核流程） | 完整 |
| [`play/developer_identity.md`](play/developer_identity.md) | https://support.google.com/googleplay/android-developer/answer/10841920 | 2026-11-24T00:02:24-06:00 | 16389 | 开发者身份验证（Play Console 账号验证流程） | 完整 |
| [`play/enforcement.md`](play/enforcement.md) | https://support.google.com/googleplay/android-developer/answer/9899234 | 2026-11-24T00:00:14-06:00 | 8840 | Enforcement Process（拒绝/下架/停用/终止、关联账号终止、申诉路径） | 完整 |
| [`play/families.md`](play/families.md) | https://support.google.com/googleplay/android-developer/answer/9893335 | 2026-11-23T23:59:44-06:00 | 19413 | Families 政策（儿童向内容、广告与 SDK、家长披露） | 完整 |
| [`play/financial_services.md`](play/financial_services.md) | https://support.google.com/googleplay/android-developer/answer/9876821 | 2026-11-24T00:00:56-06:00 | 13010 | Financial Services 政策（含订阅类金融合规） | 完整 |
| [`play/functionality.md`](play/functionality.md) | https://support.google.com/googleplay/android-developer/answer/9898783 | 2026-11-23T23:59:09-06:00 | 2169 | Functionality, Content, and User Experience（最低功能性、破碎功能、内容可用性） | 完整 |
| [`play/health.md`](play/health.md) | https://support.google.com/googleplay/android-developer/answer/9878878 | 2026-11-23T23:59:36-06:00 | 11261 | Health Content and Services（健康/医疗声明、敏感健康数据） | 完整 |
| [`play/illegal.md`](play/illegal.md) | https://support.google.com/googleplay/android-developer/answer/9878877 | 2026-11-24T00:00:44-06:00 | 903 | Illegal Activities 政策 | 完整 |
| [`play/impersonation.md`](play/impersonation.md) | https://support.google.com/googleplay/android-developer/answer/9888374 | 2026-11-24T00:00:04-06:00 | 2963 | Impersonation 政策（冒充他人/其他 App） | 完整 |
| [`play/inappropriate_content.md`](play/inappropriate_content.md) | https://support.google.com/googleplay/android-developer/answer/9878810 | 2026-11-24T00:00:49-06:00 | 15674 | Inappropriate Content（性、暴力、仇恨、恐怖） | 完整 |
| [`play/metadata.md`](play/metadata.md) | https://support.google.com/googleplay/android-developer/answer/9898842 | 2026-11-23T23:59:15-06:00 | 5050 | Metadata 政策（标题 30 字符、图标/截图/描述禁止项、不当代言人证言） | 完整 |
| [`play/misrepresentation.md`](play/misrepresentation.md) | https://support.google.com/googleplay/android-developer/answer/9888689 | 2026-11-23T23:58:57-06:00 | 2322 | Misrepresentation 政策（虚假身份、虚假开发者信息、误导性宣传） | 完整 |
| [`play/package_registration.md`](play/package_registration.md) | https://support.google.com/googleplay/android-developer/answer/16984799 | 2026-11-24T00:02:18-06:00 | 4409 | Play 包名注册（2026-09-30 起所有包名须注册） | 完整 |
| [`play/payments.md`](play/payments.md) | https://support.google.com/googleplay/android-developer/answer/9858738 | 2026-11-23T23:58:32-06:00 | 4908 | Payments 政策（数字商品须用 Google Play 结算、例外情形） | 完整 |
| [`play/payments_guidance.md`](play/payments_guidance.md) | https://support.google.com/googleplay/android-developer/answer/10281818 | 2026-11-24T00:04:57-06:00 | 18840 | Payments 政策补充指引（含 AI agentic 购买体验） | 完整 |
| [`play/policy_archive.md`](play/policy_archive.md) | https://support.google.com/googleplay/android-developer/answer/13386702 | 2026-11-24T00:02:10-06:00 | 6262 | 政策更新归档页 | 完整（仅索引，条目在 announcements） |
| [`play/policy_center_index.md`](play/policy_center_index.md) | https://support.google.com/googleplay/android-developer/topic/9858052 | 2026-11-23T23:55:24-06:00 | 432 | Policy Center 首页简介 | 不完整：仅首屏文案，无政策链接（已由 policy_hub.md 补齐） |
| [`play/policy_coverage.md`](play/policy_coverage.md) | https://support.google.com/googleplay/android-developer/answer/9899816 | 2026-11-24T00:00:28-06:00 | 3242 | Policy Coverage（政策适用范围与解释） | 完整 |
| [`play/policy_deadlines.md`](play/policy_deadlines.md) | https://support.google.com/googleplay/android-developer/table/12921780 | 2026-11-24T00:02:06-06:00 | 10096 | 政策截止日期表（生效日期一览） | 完整 |
| [`play/policy_hub.md`](play/policy_hub.md) | https://play.google/developer-content-policy/ | 2026-11-23T23:55:39-06:00 | 5147 | Play 政策总目录（Restricted Content / Impersonation / IP / Privacy, Deception and Device Abuse / SDKs / Monetization and Ads / Store Listing / Spam, Functionality and UX / Families / Enforcement） | 部分：章节与政策名齐全，链接需从 HTML 提取 |
| [`play/sensitive_permissions.md`](play/sensitive_permissions.md) | https://support.google.com/googleplay/android-developer/answer/16558241 | 2026-11-24T00:05:02-06:00 | 56706 | 敏感权限与 API（位置、全文件访问、无障碍） | 完整 |
| [`play/spam.md`](play/spam.md) | https://support.google.com/googleplay/android-developer/answer/9899034 | 2026-11-23T23:59:03-06:00 | 1833 | Spam 政策（消息垃圾、Webview 联盟垃圾、重复内容） | 完整 |
| [`play/subscriptions.md`](play/subscriptions.md) | https://support.google.com/googleplay/android-developer/answer/9900533 | 2026-11-23T23:58:25-06:00 | 8282 | Subscriptions 政策（不得误导、披露条款/价格/周期/自动续订、持续价值、免费试用与介绍优惠） | 完整；另有 2027-01-27 生效的资格类折扣条款预告 |
| [`play/subscriptions_eligibility.md`](play/subscriptions_eligibility.md) | https://support.google.com/googleplay/android-developer/answer/18204939 | 2026-11-24T00:04:52-06:00 | 8718 | 订阅资格类折扣（学生计划等）披露要求，2027-01-27 生效 | 完整（新条款预览页） |
| [`play/trader_status.md`](play/trader_status.md) | https://support.google.com/googleplay/android-developer/answer/17594752 | 2026-11-24T00:04:38-06:00 | 7181 | Play Console 交易者身份声明（2026-11 起，EU DSA） | 完整 |
| [`play/ugc.md`](play/ugc.md) | https://support.google.com/googleplay/android-developer/answer/9876937 | 2026-11-23T23:59:57-06:00 | 5726 | User Generated Content 政策（举报、屏蔽、审核） | 完整 |
| [`play/user_data.md`](play/user_data.md) | https://support.google.com/googleplay/android-developer/answer/9888076 | 2026-11-23T23:58:15-06:00 | 31060 | User Data 政策（透明披露、第三方 SDK/AI 集成、持久标识符、个人与敏感用户数据、显著披露与同意、账号数据） | 完整 |

## 没抓到 / 抓取受限

- `https://developer.apple.com/app-store/review/`（App Review 概览）：curl 返回内容过短，判定为 blocked，已记日志。不影响判定（拒绝原因在 guidelines 与 news 里都有）。
- Google 官方政策页为折叠式（accordion），转写后各小节正文被压进表格单元格，**文本完整但层级变平**；引用时按标题关键字定位，不依赖行号。
- Play「Policy Center」topic 首页（9858052）只渲染首屏文案，政策链接改由 `policy_hub.md`（play.google/developer-content-policy/）的 HTML 提取，已成体系。
