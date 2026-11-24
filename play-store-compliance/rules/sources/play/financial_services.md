<!-- source: https://support.google.com/googleplay/android-developer/answer/9876821
     fetched: 2026-11-24T00:00:56-06:00 via curl+bs4 (selector: article/main/body)
     chars: 13010
     used_for: 金融服务政策（涉及订阅/金融合规） -->

# Financial Services

Help us improve this policy article by taking a **[2-minute survey](https://google.qualtrics.com/jfe/form/SV_9YPSYrwjw03d7cG/?Source=9876821)**.

***Disclaimer:** Policy summaries and Key Considerations are overviews only; always refer to the full policy for compliance. The full policy takes precedence in case of conflict.*

We don't allow apps that expose users to deceptive or harmful financial products and services.

For the purposes of this policy, we consider financial products and services to be those related to the management or investment of money and cryptocurrencies, including personalized advice.

If your app contains or promotes financial products and services, you must comply with state and local regulations for any region or country that your app targets—for example, include specific disclosures required by local law.

Any app that contains any financial features must complete the Financial features declaration form within [Play Console](https://play.google.com/console/app/app-content/financial-features).

## Binary Options

We do not allow apps that provide users with the ability to trade binary options.

---

## Loans

**Policy Summary**

Apps that offer personal loans must meet specific requirements to protect users from predatory or misleading practices. You must clearly disclose all loan terms in your app's store listing, including the maximum annual percentage rate (APR) and the minimum and maximum repayment period. Loans must not require full repayment in 60 days or less from the date the loan is issued. You also cannot offer loans in the United States with an APR of 36% or higher. Additionally, lending apps are prohibited from accessing sensitive user data such as contacts or photos. You are responsible for complying with all applicable local laws and regulations. Please review the full policy to ensure compliance.

**Full Policy**

Personal Loans: We define personal loans as lending money from one individual, organization, or entity to an individual consumer on a nonrecurring basis, not for the purpose of financing purchase of a fixed asset or education. Personal loan consumers require information about the quality, features, fees, repayment schedule, risks, and benefits of loan products in order to make informed decisions about whether to undertake the loan.

- Examples: Personal loans, payday loans, peer-to-peer loans, title loans
- Examples not included: Mortgages, car loans, revolving lines of credit (such as credit cards, personal lines of credit)

Apps that provide personal loans, including but not limited to apps which offer loans directly, lead generators, and those who connect consumers with third-party lenders, must have the App Category set to "Finance" in Play Console and disclose the following information in the app metadata:

- Minimum and maximum period for repayment.
- Maximum Annual Percentage Rate (APR), which generally includes interest rate plus fees and other costs for a year, or similar other rate calculated consistently with local law.
- A representative example of the total cost of the loan, including the principal and all applicable fees.
- A privacy policy that comprehensively discloses the access, collection, use, and sharing of personal and sensitive user data, subject to the restrictions outlined in this policy.

We do not allow apps that promote personal loans which require repayment in full in 60 days or less from the date the loan is issued (we refer to these as "short-term personal loans").

**Key Considerations**

|  |  |
| --- | --- |
| **Do** | **Don't** |
| Provide clear and accurate disclosure of all loan terms in your app's description. | Don't mislead users with false or unclear loan terms. |
| Be properly licensed and registered to provide loans in all regions where your app is available. | Don't use your app to access or collect sensitive user data. |
| Protect user privacy by not accessing sensitive user data. |  |

---

## Earned Wage Access

Earned Wage Access: We define earned wage access loans (EWA) as a financial service that allows individuals to access a portion of their wages that have already been earned but not yet paid by their employer. Unlike traditional loans, EWA services are characterized by the following features:

- Repayment Mechanism: Repayment occurs automatically via payroll deduction or through an autopay transaction linked to the user's bank account. If the autopay transaction fails, no additional interest, penalties, or fees are charged.
- Income-Based Access: The amount available to the user is strictly limited to wages they have already earned during the current pay period, ensuring no borrowing against future income.
- Fee Structure: EWA services charge no interest and instead charge a low, flat fee or a percentage based transaction fee for usage. A reasonable fee would be minimal and transparent, reflecting the actual cost of providing the service without burdening the user, likely in the range of $1–$5 per transaction or 1–5% of the advance.
- No Debt Creation: EWA services typically do not report transactions to credit bureaus, ensuring they do not impact the user's credit score or contribute to long-term debt accumulation.

Apps that provide Earned Wage Access loans, including but not limited to apps which offer these loans directly, lead generators, and those who connect consumers with third-party lenders, must have the app category set to "Finance" in Play Console and disclose the following information in the app metadata:

- Repayment terms and conditions
- All fees, including subscription fees, transaction fees, and all other fees related to providing the loan.
- A representative example of the total cost of the loan, including all fees.
- A privacy policy that comprehensively discloses the access, collection, use, and sharing of personal and sensitive user data, subject to the restrictions outlined in this policy.

---

## General Requirements

Personal loan apps, apps with the primary purpose of facilitating access to personal loans (for example, lead generators or facilitators) or lines of credit, accessory loan or credit apps (loan calculators, loan guides, etc.), and Earned Wage Access (EWA) apps are prohibited from accessing sensitive data, such as photos and contacts. The following permissions are prohibited:

- `READ_EXTERNAL_STORAGE`
- `READ_MEDIA_IMAGES`
- `READ_CONTACTS`
- `ACCESS_FINE_LOCATION`
- `READ_PHONE_NUMBERS`
- `READ_MEDIA_VIDEO`
- `QUERY_ALL_PACKAGES`
- `WRITE_EXTERNAL_STORAGE`

Apps that utilize sensitive information or APIs are subject to additional restrictions and requirements. Please see the [Permissions policy](https://support.google.com/googleplay/android-developer/answer/9888170) for additional information.

We must be able to establish a connection between your developer account and any provided licenses or documentation proving your ability to provide financial products. Additional information or documents may be requested to confirm your account is in compliance with all local laws and regulations.

---

## Country specific requirements

Personal loan apps targeting the listed countries must comply with additional requirements and provide supplementary documentation as part of the Financial features declaration within [Play Console](https://play.google.com/console/app/app-content/finance-declaration). Apps that provide EWA loans are subject to these requirements to the extent applicable in the relevant jurisdictions. You must, upon Google Play's request, provide additional information or documents relating to your compliance with the applicable regulatory and licensing requirements.

1. **United States**
   1. In the United States, we do not allow apps for personal loans where the Annual Percentage Rate (APR) is 36% or higher. Apps for personal loans in the United States must display their maximum APR, calculated consistently with the [Truth in Lending Act (TILA)](https://www.ecfr.gov/cgi-bin/text-idx?c=ecfr&tpl=/ecfrbrowse/Title12/12cfr1026_main_02.tpl).
   2. This policy applies to apps which offer loans directly, lead generators, and those who connect consumers with third-party lenders.
2. **India**
   1. Only apps that submit a license and are on the "Digital lending apps (DLAs) deployed by Regulated Entities" list of the Reserve Bank of India (RBI) may submit personal loan apps to Google Play for review (see this [Help Center article](https://support.google.com/googleplay/android-developer/answer/16604194) for guidance).
   2. If you are not directly engaged in money lending activities and are only providing a platform to facilitate money lending by registered Non-Banking Financial Companies (NBFCs) or banks to users, you will need to accurately reflect this in the declaration.
      1. In addition, the names of all registered NBFCs and banks must be prominently disclosed in your app's description.
3. **Indonesia**
   1. If your app is engaged in the activity of Information Technology-Based Money Lending Services in accordance with OJK Regulation No. 77/POJK.01/2016 (as may be amended from time to time), you must submit a copy of your valid license for our review.
4. **Philippines**
   1. All financing and lending companies offering loans via Online Lending Platforms (OLP) must obtain a SEC Registration Number and the Certificate of Authority (CA) Number from the Philippines Securities and Exchanges Commission (PSEC).
      1. In addition, you must disclose your Corporate Name, Business Name, PSEC Registration Number, and Certificate of Authority to Operate a Financing/Lending Company (CA) in your app's description.
   2. Apps engaged in lending-based crowdfunding activities, such as peer-to-peer (P2P) lending, or as defined under the Rules and Regulations Governing Crowdfunding (CF Rules), must process transactions through PSEC-Registered CF Intermediaries.
5. **Nigeria**
   1. Digital Money Lenders (DML) must adhere to and complete the LIMITED INTERIM REGULATORY/ REGISTRATION FRAMEWORK AND GUIDELINES FOR DIGITAL LENDING, 2022 (as may be amended from time to time) by the Federal Competition and Consumer Protection Commission (FCCPC) of Nigeria and obtain a verifiable approval letter from the FCCPC.
   2. Loan Aggregators must provide documentation and/or certification for digital lending services and contact details for every partnered DML.
6. **Kenya**
   1. Digital Credit Providers (DCP) should complete the DCP registration process and obtain a license from the Central Bank of Kenya (CBK). You must provide a copy of your license from the CBK as part of your declaration.
   2. If you are not directly engaged in money lending activities and are only providing a platform to facilitate money lending by registered DCP(s) to users, you will need to accurately reflect this in the declaration and provide a copy of the DCP license of your respective partner(s).
   3. Currently, we only accept declarations and licenses from entities published under the Directory of Digital Credit Providers on the official website of the CBK.
7. **Pakistan**
   1. Each Non-Banking Finance Company (NBFC) lender can only publish one Digital Lending App (DLA). Developers who attempt to publish more than one DLA per NBFC risk the termination of their developer account and any other associated accounts.
   2. You must submit proof of approval from the SECP to offer or facilitate digital lending services in Pakistan. In addition, short-term loan apps are not permitted; however, rare exceptions may be considered when explicitly permitted by laws and regulations in Pakistan.
8. **Thailand**
   1. Personal loan apps targeting Thailand, with interest rates at or above 15%, must obtain a valid license from the Bank of Thailand (BoT) or the Ministry of Finance (MoF). Developers must provide documentation that proves their ability to provide or facilitate personal loans in Thailand. This documentation should include:
      1. A copy of their license issued by the Bank of Thailand to operate as a personal loan provider or nano finance organization.
      2. A copy of their Pico-finance business license issued by the Ministry of Finance to operate as a Pico or Pico-plus lender.
   2. All personal loan apps targeting Thailand must display the following details in the Google Play listing:
      1. The name of the loan service provider(s) licensed by the Bank of Thailand (BoT) or the Fiscal Policy Office (FPO).
      2. Legal entity name for the developer.
      3. Maximum interest rates and all fees.
   3. In addition to the above information, personal loan apps targeting Thailand, with interest rates below 15%, must also include the following:
      1. The statement "This is a non-regulated loan provider under the BoT/FPO".

Examples of common violations

Help us improve this policy article by taking a **[2-minute survey](https://google.qualtrics.com/jfe/form/SV_9YPSYrwjw03d7cG/?Source=9876821)**.

## Was this helpful?

How can we improve it?
