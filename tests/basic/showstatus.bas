90 CALL CLEAR
91 PRINT "Asking TIPI..."
100 OPEN #1:"TIPI.STATUS",DISPLAY,VARIABLE 80,INPUT
200 PRINT "TIPI Stats:"
210 PRINT "-----------"
300 INPUT #1:L$
400 PRINT L$
410 IF EOF(1) = 0 THEN 300
1000 PRINT "-----------"
1100 CLOSE #1

