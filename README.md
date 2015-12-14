# uz-kraken

[![Build Status](https://travis-ci.org/Eretic/uz-kraken.svg)](https://travis-ci.org/Eretic/uz-kraken)

Monitor tickets on uz.gov.ua

JJDecoder based on [Decoder-JJEncode](https://github.com/jacobsoo/Decoder-JJEncode)

### Example of using command line utility 

    ./kraken.py search "Киев-Пассажирский" "Харьков-Пасс"  "24.12.2015"

    Поезд 776П Киев-Пассажирский Харьков-Пасс
	    Отправление: 2015-12-24 00:14:00
	    Прибытие: 2015-12-24 08:53:00
	    Сидячий третьего класса: 73
    Поезд 114Л Мукачево Харьков-Пасс
    	Отправление: 2015-12-24 01:28:00
	    Прибытие: 2015-12-24 07:20:00
	    Люкс: 26, Купе: 23
