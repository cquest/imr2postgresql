Problème de quoting dans certains fichiers CSV
Quelques CSV ne sont pas en UTF8 mais en ISO8859-1/CP1252


PM manquantes dans le stock:

0101_2_20170512_151102_2_PM_EVT.csv : '0101', 'Bourg-en-Bresse', '2017D00282', '829180918'
0301_4_20170512_194628_2_PM_EVT.csv : '0301', 'Cusset', '2017D00113', '829483510'
0602_10_20170512_201803_2_PM_EVT.csv : '0602', 'Cannes', '2017D00212', '401901392'
0602_11_20170513_071448_2_PM_EVT.csv : '0602', 'Cannes', '2017B00579', '527677074'
0602_14_20170516_084707_2_PM_EVT.csv : '0602', 'Cannes', '2017B00586', '493363212'
0603_4_20170512_121457_2_PM_EVT.csv : '0603', 'Grasse', '2017B00392', '533349254'


PP manquantes dans le stock:

0603_4_20170512_121457_4_PP_EVT.csv : '0603', 'Grasse', '1987A00311', '332404912'
1301_1_20170512_110121_4_PP_EVT.csv : '1301', 'Aix-en-Provence', '1970A00091'

Exemples de PM avec greffe principal multiple:

   siren   | nb |          codes greffe
-----------+----+-------------------------------
 511236051 |  6 | 3302 5103 5402 6303 7501 7803
 334271491 |  3 | 0301 0901 3102
 320837677 |  3 | 1301 7501 8401
 325260347 |  3 | 0603 8305 9401
 332291228 |  3 | 7501 7801 7803
 056807712 |  3 | 1303 5103 9401
 302079462 |  3 | 1303 2202 7701
 313382293 |  3 | 1704 1708 7901
 323763789 |  3 | 0702 0702 8401


Exemples de PM sans greffe principal, mais plusieurs greffes secondaires

   siren   | nb  |            min            
-----------+-----+---------------------------
 343262622 | 131 | LIDL
 722033115 | 112 | MIM
 399226653 | 108 | AUBERT FRANCE
 339993164 |  91 | Start People
 668502966 |  81 | WURTH FRANCE
 542066238 |  81 | ETABLISSEMENT NICOLAS
 392377248 |  78 | MAXI TOYS FRANCE
 775618945 |  74 | 4MURS
 444750368 |  66 | JARDILAND ENSEIGNES
 302556832 |  65 | " ELF ANTAR FRANCE "
 310327895 |  60 | SARECTEC FRANCE
 562038216 |  58 | RAPP S.E.R.
 324501006 |  54 | PHARMA DOM
 440267177 |  50 | AXIMA REFRIGERATION
 384454690 |  45 | EURO INFORMATION SERVICES
 702021114 |  42 | DERICHEBOURG PROPRETE
 542031117 |  41 | MOBIL OIL FRANCAISE
 769800202 |  38 | HEPPNER
 318488384 |  35 | R.M.0 TRAVAIL TEMPORAIRE
 945752137 |  35 | CLEMESSY


Exemples de PP sans greffe principal, mais plusieurs greffes secondaires:

   siren   | nb |               min                |           min            
-----------+----+----------------------------------+--------------------------
 651093247 | 35 | MORAND                           |  
 352835250 |  7 | MOSBACH                          | Gilles
 301328381 |  5 | DEVAUX                           |  
 312690399 |  4 | CAFFIER                          | Anita
 332132422 |  4 | LECLERC                          |  
 323936997 |  3 | REBOURS                          | Bernard
 308072123 |  3 | CATTELIN                         | Germaine
 729401323 |  3 | COHEN                            |  
 438603946 |  3 | KLEINCLAUSS                      | Nicole
 427270129 |  3 | THEPAUT ALINE,JOSETTE,DENISE     |  
 467115069 |  3 | BERGE                            |  
 349207498 |  3 | ROZIER                           | Michel
 388711889 |  3 | CIPRIANI NEE ROMERO MARIE LOUISE |  
 315914911 |  3 | FROMAGET                         | Jean-Claude
 560703613 |  3 | RIGAL                            | Pierrot
 309956001 |  2 | SIDDIQ                           | Mohamed
 309671949 |  2 | OULD CHERCHALI PIERRE            |  
 310118278 |  2 | ERDMANN                          | Roland
 307184986 |  2 | LIENARD                          | Michel Paul Alfred Henri
 309041333 |  2 | BRUNET MARIE LAURE REINE         |  

Exemples de PP avec plusieurs greffes principaux:

   siren   | nb_pri | nb_sec |     min      |            min             
-----------+--------+--------+--------------+----------------------------
 412694374 |     10 |      0 | CASTAIGNEDE  | Laurent Christophe
 508523206 |      7 |      0 | BENCHAMA     | Mohammed
 349791475 |      7 |      0 | MOULENAT     | Philippe André Jean Pierre
 000000000 |      7 |      0 | CHAMBOURNIER | Francesco
 422221374 |      6 |      0 | FOLLET       | Jérôme Jean-Marie Nicolas
 391409018 |      5 |      0 | COTTIN       | Laurent Yves Gilbert
 333162931 |      4 |      0 | ROCCARO      | Irène
 524541596 |      4 |      0 | Dagorn       | Patricia
 309724995 |      4 |      0 | LAFLEUR      | Martial
 379377971 |      4 |      1 | LANTIGNER    | Jean Louis
 316680305 |      4 |      0 | LALET        |  
 319045290 |      4 |      0 | FICHET       |  
 382429322 |      4 |      0 | BORD         | Nadine
 314955287 |      4 |      0 | BOUCHE       | Michel
 314810789 |      3 |      0 | MORHAIM      |  
 315149880 |      3 |      0 | LOUCHARD     |  
 312739071 |      3 |      0 | NDIAYE       | Aliou
 312250160 |      3 |      0 | ESQUIVE      | Francois Remy
 314378829 |      3 |      0 | COHEN        | Jacques
 316485101 |      3 |      0 | OUDOT        |  
