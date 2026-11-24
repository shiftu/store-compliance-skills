<!-- source: https://support.google.com/googleplay/android-developer/answer/17134731
     fetched: 2026-11-24T00:01:59-06:00 via curl+bs4 (selector: article/main/body)
     chars: 6161
     used_for: 政策公告 2026-07-15（含 target API/开发者验证） -->

# Policy announcement: July 15, 2026

**Updated policies**

You'll have at least 30 days from July 15, 2026 to update your app to comply with the policy changes below. For more details, go to the [Policy Deadlines](https://support.google.com/googleplay/android-developer/table/12921780) page.

- To better protect minors, our [Age-Restricted Content and Functionality](https://support.google.com/googleplay/android-developer/answer/17036597) and [Child Safety Standards](https://support.google.com/googleplay/android-developer/answer/17122524#child_safety) policies have new requirements and restrictions for anonymous chat and random chat apps. Our [Families Policy Requirements](https://support.google.com/googleplay/android-developer/answer/17122218#families-policy) policy also now prohibits anonymous chat apps from targeting children.
- Our [SMS and Call Log Permissions](https://support.google.com/googleplay/android-developer/answer/10208820?sjid=17577182363882827718-NC&visit_id=639160341729576617-3917463334&rd=1#zippy=%2Calternatives-to-common-uses) policy will no longer permit account verification via phone call as a use case for the `READ_CALL_LOG` permission. To securely verify accounts without requiring sensitive app permissions, use the [Digital Credentials API](https://developer.android.com/identity/digital-credentials/phone-number-verification) instead, either directly or through a verification provider built upon it, or the [SMS Retriever API](https://developer.android.com/identity/sms-retriever). Please refer to [this page](https://developer.android.com/privacy-and-security/minimize-permission-requests#verify-phone-number) for additional alternative APIs.
- To meet [Android developer verification requirements](https://developer.android.com/developer-verification) and [Play Console requirements](https://support.google.com/googleplay/android-developer/answer/17125096), you must register your Play apps in Play Console. While 99% of apps on Play have been registered automatically, you should check your [Play Console Home page](https://play.google.com/console/u/0/developers/5700313618786177705/android-developer-verification) and register any remaining apps you want to continue distributing to avoid global removal from Google Play and ensure a seamless user installation experience.

  You can also use Play Console to register apps you distribute outside of Google Play to ensure they can be installed on certified Android devices.

**Clarifications**

Additionally, we've added clarifications to some of our existing policies. Because these changes aren't new or updated, our enforcement standards and practices remain the same.

- We're reframing and clarifying our [Personal Loans](https://support.google.com/googleplay/android-developer/answer/9876821#personal-loans) policy requirements for Earned Wage Access (EWA) apps to ensure that EWA services maintain the same high standards for transparency and user privacy protections as other financial service apps.
- We're clarifying that our [User Data](https://support.google.com/googleplay/android-developer/answer/10144311) requirements also apply to third-party AI integrations and that developers remain responsible for ensuring compliance with this policy, including limited use, disclosure and consent.
- We're clarifying the [Content Ratings](https://support.google.com/googleplay/android-developer/answer/9898843) policy to indicate that we don't allow unrated apps on Google Play.
- We're providing more guidance around precise and approximate locations disclosures in the [Play Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469).

**Reminders and Additional Information**

- To provide Android and Google Play users with a safe experience, Google Play requires all apps to meet the latest [target API level requirements](https://support.google.com/googleplay/android-developer/answer/11926878) by August 31, 2026. This is our regular yearly update.
- To help you catch potential issues before you submit your app for review, we've launched a **new Android skill to help you with Play Policies**. It's an open-source tool that grounds LLMs in Google Play Policies so your preferred AI assistant can evaluate your code right inside your IDE or CLI. [Read more](https://github.com/android/skills/tree/main/play/play-policy-insights).
- We're introducing a standardized numbering system across some [policies](https://support.google.com/googleplay/android-developer/answer/9898783) for better tracking and clarity. You will see these starting today, with more being updated over time.

Please review these policy updates carefully in case any of your apps are impacted. To learn more about how to comply with these changes:

- Watch this [PolicyBytes video](https://goo.gle/policybytes326), which can also be found on our [PolicyBytes Hub](https://support.google.com/googleplay/android-developer/answer/16373081).
- Register for a [Policy Webinar](https://developersonair.withgoogle.com/google-play-policy-webinars), available for multiple regions. Send in your questions in advance.
- As part of this policy refresh, Play Academy has updated two existing courses and added a new video resource to help developers better understand key policy requirements and best practices:

  - [Comply with Google Play's Age Restricted Content and Functionality Policy](https://playacademy.exceedlms.com/student/activity/1830979-comply-with-google-play-s-age-restricted-content-and-functionality-policy)
  - [Get started with your Google Play developer account](https://playacademy.exceedlms.com/student/activity/10796-get-started-with-your-google-play-developer-account)
  - [New Play Academy video on Privacy Policy best practices](https://playacademy.exceedlms.com/student/activity/1961002-build-user-trust-with-an-accurate-privacy-policy) to support developers
- Ask questions or share best practices with fellow developers in the [Google Play Developer Help Community](https://support.google.com/googleplay/android-developer/thread/450828050/policy-updates-announced-july-15-2026).

## Was this helpful?

How can we improve it?
