Adding a User
This request allows to create a user account record on a trade server.

Request format

GET /api/user/add?login=login&pass_main=password&pass_investor=password&rights=rights&group=group&name=name&company=company&language=language&city=city&state=state&zipcode=zipcode&
address=address&phone=phone&email=email&id=id&status=status&comment=comment&color=color&pass_phone=password&leverage=leverage&agent=account
 
POST /api/user/add?login=login&pass-main=password&pass_investor=password&rights=rights&group=group&name=name&company=company&language=language&city=city&state=state&zipcode=zipcode&
address=address&phone=phone&email=email&id=id&status=status&comment=comment&color=color&pass_phone=password&leverage=leverage&agent=account
{ Description of a user being created in JSON format }

Response format

{
  "retcode" : "0 Done",
  "answer" : { description }
}

Example

//--- request to the server
POST /api/user/add?group=demoforex&name=JohnSmith&leverage=100
{
  "PassMain" : "1Ar#pqkj",
  "PassInvestor" : "2Ar#pqkj",
  "MQID" : "5CD369A9",
  "Company" : "Individual",
  "Country" : "United States",
  "City" : "New York"
}
 
//--- server response
{
  "retcode" : "0 Done",
  "answer" : { 
    "Login" : "954402",
    "Group" : "demoforex",
    "CertSerialNumber" : "0",
    "Rights" : "2531",
    "MQID" : "5CD369A9",
    "Registration" : "1572956466",
    "LastAccess" : "1572956466",
    "LastPassChange" : "1572956466",
    "Name" : "JohnSmith",
    "Company" : "Individual",
...
  }
}

Request Parameters
login — login of the user account that is being added. In case no login is specified for an account (is equal to 0), the server automatically allocates a login from the available range.
pass_main or PassMain — master password of the account. The password must contain four character types: lowercase letters, uppercase letters, numbers, and special characters (#, @, ! etc.). For example, 1Ar#pqkj. The minimum password length is determined by group settings, while the lowest possible value is 8 characters. The maximum length is 16 characters. This field is required. For security reasons, it is not recommended to pass the password in the request parameters — instead, pass it in an additional body as PassMain.
pass_investor or PassInvestor — investor password of the account. The password must contain four character types: lowercase letters, uppercase letters, numbers, and special characters (#, @, ! etc.). For example, 1Ar#pqkj. The minimum password length is determined by group settings, while the lowest possible value is 8 characters. The maximum length is 16 characters. This field is required. For security reasons, it is not recommended to pass the password in the request parameters — instead, pass it in an additional body as PassInvestor.
rights — user permissions. Passed using the EnUserRights enumeration (sum of values of appropriate flags). To allow an account to be used in client terminals, enable the IMTUser::USER_RIGHT_ENABLED right for that account.
group — group in which the user account should be created. This field is required.
name — client's name. The maximum length of a client's symbol name is 128 characters (including the end-of-line character). If a string of a greater length is assigned, it will be cut to this length. This field is required.
company — name of the client's company. The maximum length of the company name is 64 characters (including the end-of-line character. A longer string will be trimmed up to this length.
language — client's language. Specified in the LANGID format used in the MS Windows (value from Prim.lang.identifier).
country — the user's country of residence.
city — user's city of residence.
state — user's state (region) of residence.
zipcode —  user's zip code.
address — the address of the user. The maximum address length is limited to 128 characters (including the end-of-line character). A longer string will be trimmed up to this length.
phone — user's phone number.
email — the email address of the user.
id — the number of a client's identity document.
status — client's status.
comment — a comment to the user The comment length is limited to 64 characters (including the end-of-line character). A longer string will be trimmed up to this length.
color — the color of the client's requests shown when handling the requests via the manager terminal.
pass_phone or PhonePassword — the user's phone password. For security reasons, it is not recommended to pass the password in the request parameters — instead, pass it in an additional body as PhonePassword.
leverage — the size of a client's leverage in the leverage from 1 to 500. This field is required.
account — the number of a user's account in an external bank. Corresponds to "Bank account" field in MetaTrader 5 Administrator terminal.
agent — the number of an agent account.
After the command parameters, you can specify the description of the parameters of the user account record in the JSON format. Parameters of the user record passed in the additional description overwrite parameters passed in the main body of the command. The complete description of the possible user parameters is provided in the "Data structure" section.

The JSON description of the user record passed when creating is the same as the description returned by the server. For example:

{
"Login" : "1023",
"Group" : "demo\demoforex",
"CertSerialNumber" : "0",
"Rights" : "483",
"Registration" : "1314700797",
"LastAccess" : "1314700797",
"LastIP" : "0.0.0.0",
"Name" : "John Smith",
...
}

Client description can be passed in the command parameters, in an additional body in the JSON format, or both at once. A description passed in an additional body has higher priority.
We strongly urge you against passing passwords in the command parameters since request addresses may be logged/cached by intermediary network devices the request passes through on its way from the client to the server. Always send passwords in an additional request body.
Response Parameters
retcode — if successful, the command returns a response code 0. Otherwise, it will return an error code.
answer — added user parameters in JSON format. The complete description of the passed client parameters is given in the "Data structure" section.
Notes
In case there are no more available ranges of logins, error 3002 is returned.
You can add a user on a trade server only when connecting to this trade server. When trying to add a user on a different server, error 3003 is returned.
When executing the command, it checks whether the entry already exists. If an account already exists, error 3004 is returned. The key field for comparison is the user login.
Before adding, the correctness of the record is checked. If the entry is incorrect, it returns the error code 3.
The error code 3006 is returned if the password of the new client is incorrect (not complex enough or does not meet the minimum length requirement specified for the client group).
The error code 8 is returned in the following cases:
The manager account does not have a permission for editing accounts
The manager account does not have a permission for the group, where the account is being created
The group, to which the account is being added, does not exist on the server
Please pay attention to the ApiData property use specifics. Acceptable fields for each of the property cell (which are always 16):

Required fields AppID and ID containing the the application ID and the property ID.
One of the fields: ValueInt, ValueUInt or ValueDouble, to determine the cell value type. If several fields are specified, the presence of the fields will be checked in the following order: ValueInt, ValueUInt, ValueDouble. The type of the last one found will be used in this case. For example, to write a value of the 'unsigned' type, specify:
{
  ...
  "ApiData": [
    {
      "AppID": "1",
      "ID": "2",
      "ValueUInt": "3",
    },
    ...
  ],
  ...
}

Accordingly, when using *_get_* methods, take a value from the ValueUInt field of the corresponding cell within the ApiData property.




IMTUser::EnUsersRights
Permissions that can be given to a user are enumerated in IMTUser::EnUsersRights.

ID

Value

Description

USER_RIGHT_NONE

0x0000000000000000

No permissions.

USER_RIGHT_ENABLED

0x0000000000000001

The user is allowed to connect.

USER_RIGHT_PASSWORD

0x0000000000000002

The user is allowed to change the password.

USER_RIGHT_TRADE_DISABLED

0x0000000000000004

Trading is disabled for the user.

USER_RIGHT_INVESTOR

0x0000000000000008

Service value for internal use.

USER_RIGHT_CONFIRMED

0x0000000000000010

User's certificate is confirmed.

USER_RIGHT_TRAILING

0x0000000000000020

The user is allowed to use trailing stop.

USER_RIGHT_EXPERT

0x0000000000000040

The user is allowed to use Expert Advisors.

USER_RIGHT_OBSOLETE

0x0000000000000080

The flag is obsolete and is not used.

USER_RIGHT_REPORTS

0x0000000000000100

The user is allowed to receive daily reports. If the permission is not enabled, daily reports are neither generated nor sent for the account.

USER_RIGHT_READONLY

0x0000000000000200

Service value for internal use.

USER_RIGHT_RESET_PASS

0x0000000000000400

The user must change password during the next connection.

USER_RIGHT_OTP_ENABLED

0x0000000000000800

The user can use OTP authentication.

USER_RIGHT_SPONSORED_HOSTING

0x0000000000002000

Brokers can pay the virtual hosting fee for their customers. The service is extremely important for traders, and the opportunity to receive a VPS for free can give them a good reason to choose your company over competitors. The availability of a broker-sponsored VPS is controlled at the individual account level. Only if this flag is enabled, the appropriate payment plan will be shown to the trader in the client terminal. For more details, please read the appropriate section.

USER_RIGHT_API_ENABLED

0x0000000000004000

The user is allowed to connect via the Web API. The flag is obsolete and is not used.

USER_RIGHT_PUSH_NOTIFICATION

0x0000000000008000

The user has enabled Push notifications from the trade server in the client terminal. The ability to subscribe to such notifications is defined by the group settings (IMTConGroup::PERMISSION_NOTIFY_*).

USER_RIGHT_TECHNICAL

0x0000000000010000

Permission for convenient work with technical accounts. Disable it for testing accounts to hide them from all managers who do not have special access to technical accounts (IMTConManager::RIGHT_ACC_TECHNICAL). Such technical accounts can be confusing for the managers working with clients, in which case hiding them can be useful.

The permission affects the visibility in the general list of accounts in the Administrator and Manager terminals, as well as in the list of online accounts in the Manager terminal.

USER_RIGHT_EXCLUDE_REPORTS

0x0000000000020000

Allows excluding an account from server reports. Like the previous permission, it is intended for more convenient work with technical accounts.

USER_RIGHT_ALL

 

End of enumeration. Corresponds to enabling of all permissions.



Data Structure
Data on users is passed in JSON format as a response to the /api/user/add, /api/user/update and /api/user/get requests.

User Parameters
Information about a user includes the following parameters:

Option Field

Type

Description

Login

Integer

The login of a user.

Group

String

User group.

CertSerialNumber

Integer

The number of a last used certificate for user authorization.

Rights

Integer

Flags of the users permissions. Passed using a value of the EnUserRights enumeration (sum of values of appropriate flags).

Registration

Integer

The user record creation date.

LastAccess

Integer

The date of the last connection using the account.

LastIP

String

The IP address from which the user last connected to the server.

LastPassChange

Integer

The date of the last password change.

Name

String

The name of the client. Obsolete field.

FirstName

String

The first name of the client.

LastName

String

The last name of the client.

MiddleName

String

The middle name of the client.

Company

String

The name of user's company.

Account

String

The number of a user's account in an external bank.

Country

String

The client's country of residence.

Language

Integer

User's language in the format LANGID used in MS Windows (value from Prim.lang.identifier).

City

String

The client's city of residence.

State

String

The user's state (region) of residence.

ZIPCode

String

The client's zip code.

Address

String

The address of the user.

Phone

String

The user's phone number.

Email

String

The email address of the user.

ID

String

The number of a user's identity document.

Status

String

Client's status.

Comment

String

A comment to the user.

Color

COLORREF

The color of the user. The color of the user. This is the color of the user's requests shown when handling the requests via the manager terminal.

PhonePassword

String

The user's phone password.

Leverage

Integer

The size of a user's leverage.

Agent

Integer

Agent account number of the user.

Balance

Float

The current balance of a client. The balance cannot be updated via this field when creating or modifying an account. To top up an account, use the /webapi_trade_balance request.

Credit

Float

The current amount of funds credited to the client.

InterestRate

Float

The amount accrued for the current month calculated based on the annual interest rate.

CommissionDaily

Float

The amount of commissions charged from a client for a day.

CommissionMonthly

Float

The total amount of commissions charged from a client for the current month.

CommissionAgentDaily

Float

The size of agent commissions charged for a client's trade operations for a day, from a daily report.

CommissionAgentMonthly

Float

The amount of agent commissions charged for a client's trade operations for the current month.

BalancePrevDay

Float

Client's balance as of the end of the previous day.

BalancePrevMonth

Float

Client's balance as of the end of the previous trading month.

EquityPrevDay

Float

A client's equity as of the end of the previous day.

EquityPrevMonth

Float

The value of a client's equity as of the end of the previous trading month.

MQID

String

MetaQuotes ID of the user.

TradeAccounts

String

User account numbers in external trading systems as [gateway ID]=[account number in the system to which the gateway is connected]. The accounts must be separated by a vertical bar "|". The total length of the accounts and IDs stored for an account is limited to 128 characters (including the end-of-line character). The maximum length of each account is limited to 32 characters (including the end-of-line character). If the total length is exceeded when you add or change the account state, the error code MT_RET_ERR_DATA will be returned.

ApiData

Array

Array of user data.

LeadSource

String

A lead source — a website a client has come from.

LeadCampaign

String

A lead campaign — name of a marketing campaign a client was attracted by.

LimitOrders

Integer

The maximum number of active (placed) pending orders allowed on the account.

LimitPositions

Integer

Maximum value of open positions allowed on the account.