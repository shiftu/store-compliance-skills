<!-- source: https://support.google.com/googleplay/android-developer/answer/9893335
     fetched: 2026-11-23T23:59:44-06:00 via curl+bs4 (selector: article/main/body)
     chars: 19413
     used_for: 家庭政策（面向儿童） -->

# Google Play Families Policies

Help us improve this policy article by taking a **[2-minute survey](https://google.qualtrics.com/jfe/form/SV_9YPSYrwjw03d7cG/?Source=9893335)**.

***Disclaimer:** Policy summaries and Key Considerations are overviews only; always refer to the full policy for compliance. The full policy takes precedence in case of conflict.*

**Policy Summary**

Apps in the Google Play Families program must protect children's privacy and comply with all applicable laws. This includes using only certified ad SDKs and prohibiting personalized advertising. If your app is for a mixed audience, you must include a neutral age screen to ensure children only see non-personalized ads. Apps must have a privacy policy that accurately reflects data collection and handling practices. Please review the full policy to ensure compliance.

**Full Policy**

The use of technology as a tool for enriching families' lives continues to grow, and parents are looking for safe, high-quality content to share with their children. You may be designing your apps specifically for children or your app may just attract their attention. Google Play wants to help you make sure your app is safe for all users, including families.

The word "children" can mean different things in different locales and in different contexts. It is important that you consult with your legal counsel to help determine what obligations and/or age-based restrictions may apply to your app. You know best how your app works so we are relying on you to help us make sure apps on Google Play are safe for families.

All apps that comply with Google Play Families policies can opt in to be rated for the [Teacher Approved program](https://playacademy.exceedlms.com/sl/91535e27), but we cannot guarantee that your app will be included in the Teacher Approved program.

#### [COLLAPSE ALL](/googleplay/android-developer/answer/9893335) [EXPAND ALL](#1&2&3&4&5&6&7&87&9)

## Play Console Requirements

**Target Audience and Content**

In the [Target Audience and Content](https://support.google.com/googleplay/android-developer/answer/9285070) section of the Google Play Console you must indicate the target audience for your app, prior to publishing, by selecting from the list of age groups provided. Regardless of what you identify in the Google Play Console, if you choose to include imagery and terminology in your app that could be considered targeting children, this may impact Google Play's assessment of your declared target audience. Google Play reserves the right to conduct its own review of the app information that you provide to determine whether the target audience that you disclose is accurate.

You should only select more than one age group for your app's target audience if you have designed your app for and ensured that your app is appropriate for users within the selected age group(s). For example, apps designed for babies, toddlers, and preschool children should only have the age group "Ages 5 & Under" selected as the age group target for those apps. If your app is designed for a specific level of school, choose the age group that best represents that school level. You should only select age groups that include both adults and children if you truly have designed your app for all ages.

**Updates to Target Audience and Content Section**

You can always update your app's information in the Target Audience and Content section in the Google Play Console. An [app update](https://support.google.com/googleplay/android-developer/answer/113476) is required before this information will be reflected on the Google Play store. However, any changes you make in this section of the Google Play Console may be reviewed for policy compliance even before an app update is submitted.

We strongly recommend that you let your existing users know if you change the target age group for your app or start using ads or in-app purchases, either by using the "What's New" section of your app's store listing page or through in-app notifications.

**Misrepresentation in Play Console**

Misrepresentation of any information about your app in the Play Console, including in the Target Audience and Content section, may result in removal or suspension of your app, so it is important to provide accurate information.

---

## Families Policy Requirements

If one of the target audiences for your app is children, you must comply with the following requirements. Failure to satisfy these requirements may result in app removal or suspension.

1. **App content:** Your app's content that is accessible to children must be appropriate for children. If your app contains content that is not globally appropriate, but that content is deemed appropriate for child users in a particular region, the app may be available in that region ([limited regions](https://support.google.com/googleplay/android-developer/answer/9899234)) but will remain unavailable in other regions.
2. **App functionality:** Your app must not merely provide a webview of a website or have a primary purpose of driving affiliate traffic to a website without permission from the website owner or administrator.
3. **Play Console answers:** You must accurately answer the questions in the Play Console regarding your app and update those answers to accurately reflect any changes to your app. This includes but is not limited to, providing accurate responses about your app in the Target Audience and Content section, Data safety section, and IARC Content Rating Questionnaire.
4. **Data practices:** You must disclose the collection of any [personal and sensitive information](/googleplay/android-developer/answer/9888076#personal_sensitive) from children in your app, including through APIs and SDKs called or used in your app. Sensitive information from children includes, but is not limited to, authentication information, microphone and camera sensor data, device data, Android ID, and ad usage data. You must also ensure that your app follows the [data practices](https://support.google.com/googleplay/android-developer/answer/11043825) below:
   - Apps that solely target children must not transmit Android advertising identifier (AAID), SIM Serial, Build Serial, BSSID, MAC, SSID, IMEI, and/or IMSI.
     - Apps solely targeted to children should not request AD\_ID permission when targeting Android API 33 or higher.
   - Apps that target both children and older audiences must not transmit AAID, SIM Serial, Build Serial, BSSID, MAC, SSID, IMEI, and/or IMSI from children or users of unknown age.
   - Device phone number must not be requested from TelephonyManager of the Android API.
   - Apps that solely target children may not request location permission, or collect, use, and transmit [precise location](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en#zippy=%2Cdata-types).
   - Apps must use the [Companion Device Manager (CDM)](https://developer.android.com/reference/android/companion/CompanionDeviceManager) when requesting Bluetooth, unless your app is only targeting device Operating System (OS) versions that are not compatible with CDM.
5. **APIs and SDKs:** You must ensure that your app properly implements any APIs and SDKs.
   - Apps that solely target children must not contain any APIs or SDKs that are not approved for use in primarily child-directed services.
     - For example, an API Service using OAuth technology for authentication and authorization whose terms of service states that it is not approved for use in child-directed services.
   - Apps that target both children and older audiences must not implement APIs or SDKs that are not approved for use in child-directed services unless they are used behind a [neutral age screen](https://support.google.com/googleplay/android-developer/answer/9285070#neutral-agescreen) or implemented in a way that does not result in the collection of data from children. Apps that target both children and older audiences must not require users to access app content through an API or SDK that is not approved for use in child-directed services.
6. **Augmented Reality (AR)****:** If your app uses Augmented Reality, you must include a safety warning immediately upon launch of the AR section. The warning should contain the following:
   - An appropriate message about the importance of parental supervision.
   - A reminder to be aware of physical hazards in the real world (for example, be aware of your surroundings).
   - Your app must not require the usage of a device that is advised not to be used by children (for example, Daydream, Oculus).
7. **Social Apps & Features:** If your apps allows users to share or exchange information, you must accurately disclose these features in the [content rating questionnaire](https://support.google.com/googleplay/android-developer/answer/9859655?visit_id=637679283344610643-1951945832&rd=1#questionnaire) on the Play Console.
   - **Social Apps:** A social app is an app where the main focus is to enable users to share freeform content or communicate with large groups of people. All social apps that include children in their target audience must provide an in-app reminder to be safe online and to be aware of the real world risk of online interaction before allowing child users to exchange freeform media or information. You must also require adult action before allowing child users to exchange personal information.
   - **Social Features:** A social feature is any additional app functionality that enables users to share freeform content or communicate with large groups of people. Any app that includes children in their target audience and has social features, must provide an in-app reminder to be safe online and to be aware of the real world risk of online interaction before allowing child users to exchange freeform media or information. You must also provide a method for adults to manage social features for child users, including, but not limited to, enabling/disabling the social feature or selecting different levels of functionality. Finally, you must require adult action before enabling features that allow children to exchange personal information.
   - Adult action means a mechanism to verify that the user is not a child and does not encourage children to falsify their age to gain access to areas of your app that are designed for adults (that is, an adult PIN, password, birthdate, email verification, photo ID, credit card, or SSN).
   - Social apps where the main focus of the app is to chat with people they do not know or to chat with people anonymously must not target children. Examples include: chat roulette style apps, dating apps, kids-focused open chat rooms, anonymous user style apps, "blindfold" apps, etc.
8. **Legal compliance:** You must ensure that your app, including any APIs or SDKs that your app calls or uses, is compliant with the [U.S. Children's Online Privacy and Protection Act (COPPA)](https://www.ftc.gov/tips-advice/business-center/privacy-and-security/children's-privacy), [E.U. General Data Protection Regulation (GDPR)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679), and any other applicable laws or regulations.

Examples of common violations

- Apps that promote play for children in their store-listing but the app content is only appropriate for adults.
- Apps that implement APIs with terms of service that prohibit their use in child-directed apps.
- Apps that glamorize the use of alcohol, tobacco or controlled substances.
- Apps that include real or simulated gambling.
- Apps that include violence, gore, or shocking content not appropriate for children.
- Apps that provide dating services or offer sexual or marital advice.
- Apps that contain links to websites that present content that violates Google Play’s [Developer Program policies](https://play.google.com/about/developer-content-policy/).
- Apps that show mature ads (for example, violent content, sexual content, gambling content) to children.

---

## Ads and Monetization

If you’re monetizing an app that targets children on Google Play, it’s important that your app follows the following Families Ads and Monetization Policy Requirements.

The policies below apply to all monetization and advertising in your app, including ads, cross-promotions (for your apps and third party apps), offers for in-app purchases, or any other commercial content (such as paid product placement). All monetization and advertising in these apps must comply with all applicable laws and regulations (including any relevant self-regulatory or industry guidelines).

Google Play reserves the right to reject, remove or suspend apps for overly aggressive commercial tactics.

**Ads requirements**

 If your app displays ads to children or to users of unknown age, you must:

- Only use [Google Play Families Self-Certified Ads SDKs](https://support.google.com/googleplay/android-developer/answer/9900633) to display ads to those users;
- Ensure ads displayed to those users do not involve interest-based advertising (advertising targeted at individual users who have certain characteristics based on their online browsing behavior) or remarketing (advertising targeted at individual users based on previous interaction with an app or website);
- Ensure ads displayed to those users present content that is appropriate for children;
- Ensure ads displayed to those users follow the Families ad format requirements; and
- Ensure compliance with all applicable legal regulations and industry standards relating to advertising to children.

**Ads format requirements**

Monetization and advertising in your app must not have deceptive content or be designed in a way that will result in inadvertent clicks from child users.

If the sole target audience for your app is children, the following are prohibited. If the target audiences of your app is children and older audiences, the following are prohibited when serving ads to children or users of unknown age:

- Disruptive monetization and advertising, including monetization and advertising that take up the entire screen or interfere with normal use and do not provide a clear means to dismiss the ad (for example, [Ad walls](https://support.google.com/googleplay/android-developer/answer/9857753#disruptive-ads)).
- Monetization and advertising that interfere with normal app use or game play, including rewarded or opt-in ads, that are not closeable after 5 seconds.
- Monetization and advertising that do not interfere with normal app use or game play may persist for more than 5 seconds (for example, video content with integrated ads).
- Interstitial monetization and advertising displayed immediately upon app launch.
- Multiple ad placements on a page (for example, banner ads that show multiple offers in one placement or displaying more than one banner or video ad is not allowed).
- Monetization and advertising that are not clearly distinguishable from your app content, such as offerwalls and other immersive ads experiences.
- Use of shocking or emotionally manipulative tactics to encourage ads viewing or in-app purchases.
- Deceptive ads that force the user to click-through by using a dismiss button to trigger another ad, or by making ads suddenly appear in areas of the app where the user usually taps for another function.
- Not providing a distinction between the use of virtual game coins versus real-life money to make in-app purchases.

Examples of common violations

- Monetization and advertising that move away from a user's finger as the user tries to close it
- Monetization and advertising that do not provide a user with a way to a exit the offer after five (5) seconds as depicted in the example below:
- Monetization and advertising that take up the majority or the device screen without providing the user a clear way to dismiss it, as depicted in the example below:

- Banner ads showing multiple offers, as depicted in the example below:

- Monetization and advertising that could be mistaken by a user for app content, as depicted in the example below:

- Buttons, ads, or other monetization that promote your other Google Play store listings but that are indistinguishable from app content, as depicted in the example below:

**Here are some examples of inappropriate ad content that should not be displayed to children.**

- **Inappropriate Media Content**: Ads for TV shows, movies, music albums, or any other media outlet that are not appropriate for children.
- **Inappropriate Video Games & Downloadable Software**: Ads for downloadable software and electronic video games that are not appropriate for children.
- **Controlled or Harmful Substances**: Ads for alcohol, tobacco, controlled substances, or any other harmful substances.
- **Gambling**: Ads for simulated gambling, contests or sweepstakes promotions, even if free to enter.
- **Adult and Sexually Suggestive Content**: Ads with sexual, sexually suggestive and mature content.
- **Dating or Relationships**: Ads for dating or adult relationship sites.
- **Violent Content**: Ads with violent and graphic content that is not appropriate for children.

**Ads SDKs**

If you serve ads in your app and your target audience only includes children, then you must use only [Families self-certified ads SDK](https://support.google.com/googleplay/android-developer/answer/9900633/) versions. If the target audience for your app includes both children and older users, you must implement age screening measures, such as a [neutral age screen](https://support.google.com/googleplay/android-developer/answer/9285070#neutral-agescreen), and make sure that ads shown to children come exclusively from Google Play self-certified ads SDK versions.

Please refer to the [Families Self-Certified Ads SDK Program](https://support.google.com/googleplay/android-developer/answer/9900633/) policy page for more details on these requirements and refer [here](https://support.google.com/googleplay/android-developer/answer/9283445) to see the current list of Families Self-Certified ads SDK versions.

If you use AdMob, refer to the [AdMob Help Center](https://support.google.com/admob/answer/6223431) for more details on their products.

It is your responsibility to ensure your app satisfies all requirements concerning advertisements, in-app purchases, and commercial content. Contact your ads SDK provider(s) to learn more about their content policies and advertising practices.

**Key Considerations**

|  |  |
| --- | --- |
| **Do** | **Don't** |
| Adhere to laws like COPPA and GDPR regarding children's data. | Don't serve personalized ads to children. |
| Use certified ad SDKs for apps serving ads to children. | Don't collect personal data persistent identifiers (like AAID or IMEI)from children. |
| Use a neutral age screen if your app's audience is mixed. | Don't use unapproved SDKs that are not certified for use in child-directed services. |
| Ensure your privacy policy accurately explains your app's data collection and handling practices. | Don't include inappropriate content such as adult themes, excessive violence, or other inappropriate content. |
| Accurately declare your app's target age group in Play Console. |  |

Help us improve this policy article by taking a **[2-minute survey](https://google.qualtrics.com/jfe/form/SV_9YPSYrwjw03d7cG/?Source=9893335)**.

## Was this helpful?

How can we improve it?
