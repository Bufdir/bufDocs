---
tags:
  - Ekstern
  - API
  - Reindex
---

# Reindex dokumentasjon

OBS: Denne er XML versjonen av API. Pr 08.11.2023 er dette det vi har å forholde oss til, men det er bedt om et rest api med json isteden fra reindex.

Reindex har kun sendt et .txt document med dokumentasjon.

## References
Authentication
No authentication is used - open access.

endpoint : https://nbbf.reindex.net/BUF/rss/rxsearch.php

parameter "command"
- record : return specific record. Must use parameter "id" from localnumber in field 001
- termlist : return list of facet terms. Must use parameter "query" for search terms
- search : return resultset. Must use parameter "query" for search terms.  Parameter "num" and parameter "start" is used for paging.

### Examples
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002452
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002723
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002552
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00000904
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=norsk
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=wrd=rundskriv
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=Barnevernet.+Til+barnets+beste
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=Barn&start=2&num=5
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002452
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=wrd=rundskriv&start=1&num=5
### Sort
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=barn&num=20&start=0&sort=date:0 
### Links
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00000441

### SDI list
https://nbbf.reindex.net/BUF/rss/Api.php?Focus=ApiSDIList&Type=Portal


https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002452
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002723
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002552
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=norsk
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=Barnevernet.+Til+barnets+beste
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=Barn&start=2&num=5
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=lko=BUFDIR&start=0&num=50
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00002452
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=lko=BUFDIR&start=0&num=50
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=ettervern&start=25&num=25

https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=termlist&query=atferd
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=atferd%20and%20lem=%22Barn%22&num=25&start=0&sort=date:0


### Sort
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=barn&num=20&start=0&sort=date:0 
### Links
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=record&id=BUF00000441

### SDI list
https://nbbf.reindex.net/BUF/rss/Api.php?Focus=ApiSDIList&Type=Portal
https://nbbf.reindex.net/BUF/rss/rxsearch.php?command=search&query=fosterhjem+and+fo%3DBacke-Hansen%2C+Elisabeth+and+fo%3DMadsen%2C+Christian+and+fo%3DHvinden%2C+Bj%C3%B8rn+and+fo%3DHvinden%2C+Bj%C3%B8rn+and+fo%3DMadsen%2C+Christian+and+sp%3Dnob+and+fo%3DBacke-Hansen%2C+Elisabeth&num=25&start=0

### Publication list
/BUF/rss/rxsearch.php?command=search&query=lko=BUFDIR&num=10&start=0&sort=date:0 

### Status
### News list 
Nyhedsliste /BUF/rss/Api.php?Focus=newslistall

