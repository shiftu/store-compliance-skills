<!-- source: https://support.google.com/googleplay/android-developer/answer/16984799
     fetched: 2026-11-24T00:02:18-06:00 via curl+bs4 (selector: article/main/body)
     chars: 4409
     used_for: Play 包名注册（2026-09-30 起强制） -->

# Registering Play package names

Developers with a Google Play Console account will need to complete two tasks to comply with Android developer verification requirements:

- Verify your identity
- Register your app package names

Effective September 30, 2026, all Play packages must be registered to meet Android developer verification requirements. Apps not registered by Sep 30, 2026 will be removed from Play pursuant to the [Play Console Requirements policy](https://support.google.com/googleplay/android-developer/answer/10788890).

## Verify your identity

If you had successfully completed identity verification at a previous time, you will not need to go through this step again. If you are unsure about the state of your identity verification, check your current account information in Play Console on the **Developer account** page (**Manage account > Account details**).

Learn more about [verifying your developer identity in Play Console](https://support.google.com/googleplay/android-developer/answer/10841920).

## Register your app package names

Google will attempt to auto-register both existing and new Play apps according to the package name eligibility rules:

|  |  |  |
| --- | --- | --- |
| **Scenario** | **Rule for auto-registration** | **Rule for other developers** |
| Majority key holder | The key that accounts for over 50% of total known installs has priority. | All other developers must submit a request. |
| 50+ installs | If no single key has >50% of installs, all keys with 50 or more installs are eligible to register the package name. | Developers with keys with fewer than 50 installs must submit a request. |
| Under 50 installs | If no keys meet the 50-install threshold, any key can be used on a first-come, first-served basis. | After the first developer registers, other developers must submit a request. |

Requests to register a package name can be made through Play Console.

You will see a notification about the registration status of your apps above the app list on the Play Console **Home** page. Navigate to the **Android developer verification** page to view registration status information for individual apps.

**Note**: You will only receive notifications about the registration status of your apps if you have completed identity verification in Play Console.

## Auto-registration status

If all package names have been successfully auto-registered, no further registration action is required for the corresponding apps. You may proceed to register any Android apps that you distribute outside of Google Play.

Learn how to [register apps distributed outside of Google Play](https://support.google.com/googleplay/android-developer/answer/16761053).

If some or all of your package names are not successfully auto-registered, you have the option of registering these manually. Hover your cursor over each app on the list, and follow the guidance to register the package name.

## Manual registration of package names

In a small number of cases, app package names will need to be manually registered, and a draft package name will be created for each of these Play apps.

1. Click **Add key**.
2. In the list of eligible keys that appear, select your app’s public certificate and click **Add key**.
3. Click **Get Started** to **Sign and upload an APK.**
4. Play Console will provide you with a snippet that you will need to copy and add to an APK's asset folder. You'll then need to sign the APK and upload it in Play Console. The link to a sample project in your Play Console lets you view the required file structure.
5. You will receive an email once your package name has been successfully registered. You will also be able to view the registration status of your package name and keys in Play Console.

**Note**: You do not need to upload the actual APK.

## Ineligible keys

There may be instances where your signing key is not eligible to register the package name as determined by the package name eligibility rules described above. In this situation, you will be required to submit a request to use the package name. Unless you have a legitimate reason to share the package name, we recommend adopting a new one.

## Get help

[Contact us](https://support.google.com/android-developer-console/contact/package_registration_issue) for more help with Android developer verification in Play Console.

## Was this helpful?

How can we improve it?
