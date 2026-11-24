<!-- source: https://developer.android.com/google/play/age-signals/use-age-signals-api
     fetched: 2026-11-24T00:04:46-06:00 via curl+bs4 (selector: article/main/body)
     chars: 1886
     used_for: Play Age Signals API（年龄保证） -->

Play Age Signals API v0.0.6 is available now globally for you to request an age range from users within your app. It will start to return responses for all users by December 11, 2026. In the meantime, [v0.0.4](https://developer.android.com/google/play/age-signals/v4/overview) will also continue to return responses in selected regions. For region-specific information, see [Regional age-related protections on Play](https://developer.android.com/distribute/age-appropriate-experiences/regional-protections).

- [Android Developers](https://developer.android.com/)
- [Google Play](https://developer.android.com/distribute)
- [Play Age Signals](https://developer.android.com/google/play/age-signals)

# Use Play Age Signals API (beta) Stay organized with collections Save and categorize content based on your preferences.

By using the Play Age Signals API (beta), you agree to the [terms of service](/google/play/age-signals/overview#terms-service)
and you agree to comply with all [Google Play developer policies](https://play.google/developer-content-policy/).

To request a user's age range and sharing status, you call the Play Age Signals
API (beta) from your app at runtime. The default age ranges the API returns
are 0-12, 13-15, 16-17, and 18+, but you can receive [custom age ranges](/google/play/age-signals/understand-age-signals-responses#custom-age-ranges).

## Integrate Play Age Signals API into your app

The Play Age Signals API is supported on phones, foldables, and tablets running
Android 6.0 (API level 23) and higher. To integrate the Play Age Signals API
into your app, add the following dependency to your app's `build.gradle` file:

```
implementation 'com.google.android.play:age-signals:0.0.6'
```

[Previous

arrow\_back

Overview](/google/play/age-signals/overview)

[Next

Request age signals

arrow\_forward](/google/play/age-signals/request-age-signals)
