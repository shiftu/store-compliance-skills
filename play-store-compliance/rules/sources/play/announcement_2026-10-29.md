<!-- source: https://support.google.com/googleplay/android-developer/answer/18100766
     fetched: 2026-11-24T00:01:47-06:00 via curl+bs4 (selector: article/main/body)
     chars: 7899
     used_for: 政策公告 2026-10-29（最新一批变更） -->

# Policy announcement: October 29, 2026

You'll have at least 30 days from October 29, 2026 to update your app to comply with the new and updated policy changes below. For more details, go to the [Policy Deadlines](https://support.google.com/googleplay/android-developer/table/12921780) page.

**New policies**

- [Local Network Permission](https://support.google.com/googleplay/android-developer/answer/16909972#local_network): This permission is restricted to apps that need it for core functionality when device pickers are insufficient. Apps targeting Android 17 or higher (API 37+) must submit a Play Console declaration to use this permission.
- [Manage Contacts Permission](https://support.google.com/googleplay/android-developer/answer/16909972#manage_contacts): This permission is restricted to apps that need it for core functionality when system pickers are insufficient and apps must submit a Play Console declaration to use it. All other apps must use narrowly scoped platform intents.
- [AppFunctions API](https://support.google.com/googleplay/android-developer/answer/16909972#appfunctions): Developers building AppFunctions must comply with all existing Google Play policies. AppFunctions are strictly prohibited from deceiving or manipulating AI agents, bypassing security controls, or interfering with other applications.

**Updated policy**

- [Subscriptions with ongoing eligibility-based discounts](https://support.google.com/googleplay/android-developer/answer/18204939): Subscriptions with ongoing eligibility-based discounts, such as student plans, must clearly disclose eligibility criteria, the verification process, and post-eligibility pricing and benefit changes.

**Clarifications** *(Our enforcement standards and practices remain the same)*

- [Permissions and APIs that Access Sensitive Information](https://support.google.com/googleplay/android-developer/answer/16558241)

  - [Location Permission](https://support.google.com/googleplay/android-developer/answer/16909972#location-permissions): As a reminder, this policy was announced last April and will become mandatory on January 27, 2027. To help you be prepared, we've clarified and added helpful information to the [upcoming policy](https://support.google.com/googleplay/android-developer/answer/16909972#location-permissions). Apps must use the minimum location scope necessary for its core functionality. For apps targeting Android 17 (API 37+), this includes mandatory use of the Android location button for one-time or infrequent location requests. Apps using `ACCESS_FINE_LOCATION` must complete a Play Console declaration to justify why coarse location or the location button is insufficient.
  - [All Files Access Permission](https://support.google.com/googleplay/android-developer/answer/16558241#all_files): We've reiterated minimum scope principles to support developer comprehension of the use of the `MANAGE_EXTERNAL_STORAGE` permission.
  - [AccessibilityAPI](https://support.google.com/googleplay/android-developer/answer/16558241#accessibility): Clarified the policy summary on the `isAccessibilityTool` flag usage and disclosure requirements based on app designation.
- [Deceptive Behavior](https://support.google.com/googleplay/android-developer/answer/17006354): Clarified that developers and apps cannot engage in behaviors that manipulate the app review process.
- [Families Self-Certified Ads SDK Program](https://support.google.com/googleplay/android-developer/answer/9900633): New applicants can now join this program. Review the list of participating SDKs and self-certified versions in the [Help Center](https://support.google.com/googleplay/android-developer/answer/12955712) and in [SDK Index](https://play.google.com/sdks).
- [Cryptocurrency](https://support.google.com/googleplay/android-developer/answer/16329703): Expanded Hong Kong licensing requirements to include the Virtual Asset Trading Platform license, and introduced an "Additional Options" section for apps qualifying for local regulatory exemptions.
- [Use of SMS or call log permission groups](https://support.google.com/googleplay/android-developer/answer/10208820)

  - Added an exception allowing Government or Authorized Mobile Network Operator apps to use the `READ_CALL_LOG` permission for Quality of Service reporting and clarified that apps utilizing the backup and restore exception must demonstrate the ability to restore data back to the device's default handler.
  - Added the [SMS User Consent API](https://developers.google.com/identity/sms-retriever/user-consent/overview) as a privacy-preserving alternative for account verification. As a reminder, on January 27, 2027, account verification via phone call will no longer be a permitted use case for the `READ_CALL_LOG` permission and you must use an [alternative API](https://developer.android.com/privacy-and-security/minimize-permission-requests#phone-calls-text-messages) instead.
- [Payments](https://support.google.com/googleplay/android-developer/answer/9858738): We're providing [additional guidance](https://support.google.com/googleplay/android-developer/answer/10281818#AI_agentic_experience) on how our Payments policy applies to Google Play apps that facilitate digital purchases through AI or agentic experiences.

**Reminders and Additional Information**

- We're launching [Play Age Signals](https://developer.android.com/google/play/age-signals/use-age-signals-api), a new privacy-friendly, age-appropriate experience for families that will be available globally to all developers. Use The Play Age Signals API to tailor features, content, and safety settings to your audience.
- If you sell into or out of Japan, you must complete authorization by December 1st, 2026, or your payments will be held globally. Find out if this requirement applies to you and learn how to complete the [authorization form](https://support.google.com/paymentscenter/answer/17595997).
- Starting in November 2026, you must declare your [trader status](https://support.google.com/googleplay/android-developer/answer/17594752) in Play Console in accordance with new Console requirements.
- As recently [announced](https://developer.android.com/docs/quality-guidelines/car-app-quality#sep-26), the games category has graduated from beta to general availability. All developers who want to build games for cars can now publish to the open testing and production tracks on Google Play for these form factors.
- We recently [announced](https://android-developers.googleblog.com/2026/08/app-quality-memory-optimization-secure-onboarding.html) a February 2027 compliance deadline for [new app quality requirements](https://support.google.com/googleplay/android-developer/answer/17492799) regarding memory and code optimization thresholds. Please review these requirements to maintain your app's visibility and publishing capabilities on Google Play.
- We have updated our [Android XR app quality guidelines](https://developer.android.com/docs/quality-guidelines/android-xr) for Immersive and Augmented experiences. Please review these guidelines if you are building apps for XR headsets, Wired XR Glasses, or Audio & Display Glasses.

Please review these policy updates carefully in case any of your apps are impacted. To learn more about how to comply with these changes:

- Watch this [PolicyBytes video](https://goo.gle/policybytes426), which can also be found on our [PolicyBytes Hub](https://support.google.com/googleplay/android-developer/answer/16373081).
- Register for a [Policy Webinar](https://developersonair.withgoogle.com/google-play-policy-webinars), available for multiple regions. Send in your questions in advance.
- Ask questions or share best practices with fellow developers in the [Google Play Developer Help Community](https://support.google.com/googleplay/android-developer/thread/475020766).

## Was this helpful?

How can we improve it?
