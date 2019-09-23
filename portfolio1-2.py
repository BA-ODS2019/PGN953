#!/usr/bin/env python3

#Importerer biblioteket pandas, da vi er nødt til at importerer det for at kunne bruge det
#der findes mange biblioteker og det vil kræve for meget hukommelse hvis Python kører dem alle
import pandas as pd

#OPGAVE 2
#Læser data fra filen ind i en dataframe
data = pd.read_csv("~/Downloads/titanic.csv") 
#for at se de fem første linjer inkl. headers, så bruger vi data.head
#for at se alle linier skrives print(data())
print(data.head())

#Viser maksimalt 100 rækker
pd.set_option('display.max_rows', 100)

#OPGAVE 2.A
#viser den deskriptive statistik (f.eks. gennemsnit, standard afvigelse og max)
#count= Den samlede værdi
#mean= Gennemsnittet
#std= Standard afvigelse - siger noget om hvor langt fra gennemsnittet folk normalt ligger
#min= Mindste værdien
#25%, 50% 75%= Hvilken værdi (og derunder) skal man have med for at udvælge n% af ens data
#max= Den maksimale værdi
print(data.describe())
#printer en tom linje og giver derved et mellemrum
print()

#OPGAVE 3.A
#Filtrerer i datasættet, så kun de overlevende er tilbage.
#vi skriver 1 da det repræsenterer de overlevende (0 repræsenterer de døde.)
survivors = data[data.Survived == 1]
#printer slutresultatet af værdien af vores variabel.
print(survivors.count())
print()

#OPGAVE 3.B
#viser gennemsnits alderen for passagerne
print("Gns alder:", data.describe()["Age"]["mean"])

#OPGAVE 3.C
#viser median alderen
print("median alder:", data.median()["Age"])
print()

#OPGAVE 3.D
#Vi deler Name op med mellemrum og tager det sidste element for at få efternavnet
last_name_groups = data.groupby(data.Name.str.split(" ").str[-1])
count_frame = last_name_groups.Name.count()
#tilføjer navn for "count" kolonnen
count_frame = count_frame.reset_index(name='count')
#Sorterer baglæns og printer
count_frame = count_frame.sort_values(['count'], ascending=False)
print(count_frame)
print()

#OPGAVE 3.E
#Hvor meget betalte hver klasse i gennemsnit for at overleve?
print(pd.pivot_table(data, columns='Pclass', values='Fare', index='Survived'))

#OPGAVE 4.A
#Viser hvor mange der rejste på hhv. 1., 2., og 3. klasse:
#Viser Pivot tabel, fra kolonnen Pclass, og tæller antal navne udfra hver klasse. 
#Vi bruger værdien Name, da vi ikke kan gøre brug af Pclass to gange.
#\n laver en ny linje (samme resultat som at skrive print())
print('\nPassengers per class:')
print(pd.pivot_table(data, columns='Pclass', values='Name', aggfunc='count'))
print()

#OPGAVE 4.B
#Viser pivot tabel, hvor vi ser gennemsnittet for antal overlevende pr. klasse. 
#Herved kan vi så se at 3. klasse havde mindst chance for at overleve = størst dødelighed

#Vi valgte at bruge gennemsnittet, da det ikke er samme antal der rejste på hver klasse
#Derved får vi et mere præcist resultat mht. hvilken klasse der havde den største dødelighed
#end hvis vi havde taget summen af passengerene fra hver klasse. 
print(pd.pivot_table(data, values=['Survived'], columns=['Pclass']))
print()


