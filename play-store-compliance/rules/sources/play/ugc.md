<!-- source: https://support.google.com/googleplay/android-developer/answer/9876937
     fetched: 2026-11-23T23:59:57-06:00 via curl+bs4 (selector: article/main/body)
     chars: 5726
     used_for: 用户生成内容政策 -->

# User Generated Content

***Disclaimer:** Policy summaries and Key Considerations are overviews only; always refer to the full policy for compliance. The full policy takes precedence in case of conflict.*

**Policy Summary**

Apps with user-generated content must have robust moderation to ensure a safe environment. You must provide clear terms of use, an in-app system for reporting objectionable content, and a function for users to block others. Incidental sexual content must be filtered by default and restricted from minors. Please review the full policy to ensure compliance.

**Full Policy**

User-generated content (UGC) is content that users contribute to an app, and which is visible to or accessible by at least a subset of the app's users.

Apps that contain or feature UGC, including apps which are specialized browsers or clients to direct users to a UGC platform, must implement robust, effective, and ongoing UGC moderation that:

- Requires users accept the app's terms of use and/or user policy before users can create or upload UGC;
- Defines objectionable content and behaviors (in a way that complies with Google Play Developer Program Policies), and prohibits them in the app’s terms of use or user policies;
- Conducts UGC moderation, as is reasonable and consistent with the type of UGC hosted by the app. This includes providing an in-app system for reporting and blocking objectionable UGC and users, and taking action against UGC or users where appropriate. Different UGC experiences may require different moderation efforts. For example:
  - Apps featuring UGC that identify a specified set of users through means such as user verification or offline registration (for example, apps exclusively used within a specific school or company, etc.) must provide in-app functionality to report content and users.
  - UGC features that enable 1:1 user interaction with specific users (for example, direct messaging, tagging, mentioning, etc.) must provide an in-app functionality for blocking users.
  - Apps that provide access to publicly accessible UGC, such as social networking apps and blogger apps, must implement in-app functionality to report users and content, and to block users.
  - In the case of augmented reality (AR) apps, UGC moderation (including the in-app reporting system) must account for both objectionable AR UGC (for example, a sexually explicit AR image) and sensitive AR anchoring location (for example, AR content anchored to a restricted area, such as a military base, or a private property where AR anchoring may cause issues for the property owner).
- Provides safeguards to prevent in-app monetization from encouraging objectionable user behavior.

#### **Incidental Sexual Content**

Sexual content is considered “incidental” if it appears in a UGC app that (1) provides access to primarily non-sexual content, and (2) does not actively promote or recommend sexual content. Sexual content defined as illegal by applicable law and [child endangerment](https://support.google.com/googleplay/android-developer/answer/9878809) content are not considered “incidental” and are not permitted.

UGC apps may contain incidental sexual content if all of the following requirements are met:

- Such content is hidden by default behind filters that require at least two user actions in order to completely disable (for example, behind an obfuscating interstitial or precluded from view by default unless “safe search” is disabled).
- Children, as defined in the [Families policy](https://support.google.com/googleplay/android-developer/answer/9893335), are explicitly prohibited from accessing your app using age screening systems such as a [neutral age screen](https://support.google.com/googleplay/android-developer/answer/9867159?visit_id=637661037575013539-1915084824&rd=1#neutral-agescreen) or an appropriate system as defined by applicable law.
- Your app provides accurate responses to the content rating questionnaire regarding UGC, as required by the [Content Ratings policy](https://support.google.com/googleplay/android-developer/answer/9898843).

Apps whose primary purpose is featuring objectionable UGC will be removed from Google Play. Similarly, apps that end up being used primarily for hosting objectionable UGC, or that develop a reputation among users of being a place where such content thrives, will also be removed from Google Play.

Examples of common violations

- Promoting sexually explicit user-generated content, including implementing or permitting paid features that principally encourage the sharing of objectionable content.
- Apps with user generated content (UGC) that lack sufficient safeguards against threats, harassment, or bullying, particularly toward minors.
- Posts, comments, or photos within an app that are primarily intended to harass or single out another person for abuse, malicious attack, or ridicule.
- Apps that continually fail to address user complaints about objectionable content.

**Key Considerations**

|  |  |
| --- | --- |
| **Do** | **Don't** |
| Require users to accept your app's terms of use before they create or upload UGC. | Don't allow objectionable content to go unmoderated or unaddressed. |
| Provide a user-friendly, in-app system for reporting objectionable content and users. | Don't promote or recommend sexual content in your app. |
| Implement a user-blocking function for one-on-one interactions. | Don't allow minors to access apps that may contain sexual content. |
| Hide incidental sexual content behind a filter that is on by default and requires multiple actions to disable. | Don't build an app whose primary purpose is to host objectionable UGC. |

## Was this helpful?

How can we improve it?
