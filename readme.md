# Our complex smtp service

* run AE, AU, BE, then click [this demo query](http://127.0.0.1:5000/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi!this%20is%20the%20first%20message%20from%20Alice!) as alice

| role  | components                            | port  |
| ----- | ------------------------------------- | ----- |
| Alice | HTTP Client                           | --    |
| AU    | __HTTP Server(Alice)__ + SMTP Client      | 5001  |
| AE    | __SMTP Server__ + SMTP Client             | 10080 |
| BE    | __SMTP Server__ + __POP3 Server__ = Mixed Server | 10079 |
| BU    | __HTTP Server(bob)__ + POP3 Client        | 5000  |
| Bob   | HTTP Client                           | --    |

# Test this app
## test locally
* you can send http requests with [`postman`](https://www.postman.com/downloads/) (recommended) or any web browser.
* send message: [http://localhost:5001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis020210439142018!](http://localhost:5001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis020210439142018!)
* retrieve messages: [http://localhost:5000/email?from=127.0.0.1:1007](http://localhost:5000/email?from=127.0.0.1:10079)

## test online demo
* you can click this link to send a demo message:[http://169.51.206.152:30001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis020210439142018](http://169.51.206.152:30001/email?from=127.0.0.1:10080&to=127.0.0.1:10079&message=hi,nowis020210439142018)
* click this link to retrieve messages: [http://169.51.206.152:30000/email?from=127.0.0.1:10079](http://169.51.206.152:30000/email?from=127.0.0.1:10079)

# Notes
1. Messages will be deleted by default once you retrieved them.
1. There's ~1s delay when sending/retrieving messages. This is because SMTP clients and POP3 clients will wait for banners from server, but BE will not send any data after the connection has established. 
