GET /api/position/get_batch?login=logins&group=groups&ticket=tickets&symbol=symbols
POST /api/position/get_batch?login=logins&group=groups&ticket=tickets&symbol=symbol
POST /api/position/get_batch?symbol=symbol
{
  "ticket": [
    1012,
    4034
  ],
  "group": [
    demoforex-eur,
    demoforex-usd
  ],
  "ticket": [
    96639,
    13549
  ],
} 

Request Parameters
login — the list of logins, the positions of which you want to receive. A commas separated list. Can also  be specified as an array in the POST request body.
group — the list of groups, for users from which you want to receive positions. You can specify one group, several groups (comma separated) or a group mask. The mask is specified using characters "*" (any value) and "!" (exception). For example: "demo*,!demoforex" - all groups whose names begin with 'demo', except for the group demoforex. Groups Can also be specified as an array in the POST request body.
ticket — the list of order tickets to receive. Can be specified as an array in the POST request body.
symbol — the symbol positions for which you want to receive. You can specify multiple symbols separated by commas. Only make sense in combination with the 'login' or 'group' parameter.
Operations can be requested with only one parameter: by logins, by groups, or by tickets. You cannot specify all the three parameters together.

esponse Parameters
retcode — if successful, the command returns the response code 0. Otherwise, an error code is returned.
answer — position array in JSON format. The complete description of the passed position parameters is provided under the Data Structure section.
Note
The request only works with open positions on the client's account. The history of positions is formed on the side of client terminals based on the history of trades. It is impossible to obtain it.

