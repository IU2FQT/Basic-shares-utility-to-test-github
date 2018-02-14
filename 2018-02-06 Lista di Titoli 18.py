# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 12:42:21 2017

@author: FP
"""

# Aggiungo un commendo per vedere come funziona la branch di github


# Load APIs
import numpy as np
import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import time
import csv
import matplotlib.pyplot as plt
import seaborn as sns

# Inizio e fine del periodo di analisi
global path
path='C:\\0_Fabio\\Py Shares Data Manager\\Files\\'

# Impostazioni di formati e stili
pd.options.display.float_format = '{:,.3f}'.format #imposta il formato con , e quattro decimali per la formattazione dei df
# classi deoi colori del caratteri
class fg: #Colore dei caratteri del testo
    BLACK   = '\033[30m' 
    RED     = '\033[31m' 
    GREEN   = '\033[32m' 
    YELLOW  = '\033[33m' 
    BLUE    = '\033[34m' 
    MAGENTA = '\033[35m' 
    CYAN    = '\033[36m' 
    WHITE   = '\033[37m' 
    RESET   = '\033[39m' 
class bg: #colore del testo in background
    BLACK   = '\033[40m' 
    RED     = '\033[41m' 
    GREEN   = '\033[42m' 
    YELLOW  = '\033[43m' 
    BLUE    = '\033[44m' 
    MAGENTA = '\033[45m' 
    CYAN    = '\033[46m' 
    WHITE   = '\033[47m' 
    RESET   = '\033[49m' 
class style: #stile del testo
    BRIGHT    = '\033[1m' 
    DIM       = '\033[2m' 
    NORMAL    = '\033[22m' 
    RESET_ALL = '\033[0m'

def Load_tick(lista, start, end):
    """ Funzione che scarica una lista di titoli da Yahoo finance.
        
    Dal momento che la connessione da internet non sempre và a buon fine itero per un
    numero Max di volte, poi passo al titolo successivo. Al termione della esecuzione
    rende un DataFrame con le quotazioni dei titoli che è riuscito a scaricare ed un secondo DataFrame
    con la lista dei titoli che non sono stati scaricati. L'utente deciderà se ritentare.       
    """    
    j=0 # contatore del numero dei tentativi fatti di scaricare il dato
    #Max=math.ceil(len(lista)/8) # numero massimo di tentativi di download, normalmente per 30 titoli bastano 3 iterazioni per scaricare tutto
    Max=3
    df=pd.DataFrame([]) #dataframe nel quale mettero i dati sull'anadamento dei titoli  
    while not(lista.empty) and j<Max:
        j+=1
        print('\n')
        print('1. Lista dei titoli da scaricare (%i tentativo di %i): \n' %(j, Max))
        print(lista)
        print('\n')
        for i in lista: # i è il ticker da scaricare
            try:
                tick_df=pdr.get_data_yahoo(i, start, end) # dati estratti da internet con Pandas_Datareader 
                tick_df['Tick']=i # aggiungo al df con i dati del titolo il ticker del titolo
                df=pd.concat([df, tick_df]) # Concateno il df_tick del tick che ho appena scaricato ai dati di tutti i tick scaricati fino ad ora
                print (i, ': OK downloaded') # confermo di avere scaricato il tick
                lista=lista[lista != i] # rimuovo il tick che ho appena scaricato dalla lista dei tick da scaricare
            except:
                print (i, 'Failed download, will try again') # nel caso in cui non abbia ricevuto dati dal server yahoo lascio il tick nella lista in modo da riprovare con il loop esterno ed avviso l'utente che non ho reperito il dato                
    #del tick_df cancello il df dell ultimo tic
    return df, lista 

# Funziona che scarica da Yahoo una lista di tickers
def Load_listino():
    """ Upload di una lista di titoli i cui ticker sono contenuti in un file Excel
    
    La funzione carica dal server di Yahoo finance i dati di borsa della lista dei titoli
    contenuti in uyn file Excel. Il file si trova nella stessa directory in cui si trova questo script.
    Viene utilizzato il foglio-1 dello spreadsheet. I titoli vengono scaricati dalla funzione Load_tick
    che riceve la lista comnpleta dei titoli e restituisce il DataFrame dei titoli scaricati. Questa funzione
    si occupa principalmente della gestione dei titoli non scaricati per dare all'utente la possibilità di
    eseguire molteplici tentativi nel caso in cui il server non risponda, oppure di rinunciare.
    """
    # Initialize
    a=path+'Tick_list.xls'
    listino=pd.read_excel(a, sheet_name='Sheet1') # File in formato XLS dei titoli da scaricare, con la aggiunta dei nomi e di altri possibili attributi di selezione (ad esempio se sono bancari, su quale borsa si trovano etc)
    lista=listino['Tick'] # lista dei titoli da scaricare, i titoli vengono rimossi mano a mano che vengono scaricati
    shares=pd.DataFrame([]) #creo il df che conterrà i dati dei titoli
    risposta='Y' 

    # Input data di inizio e fine della serie storica
    start=input('\tInserire la data di inizio nel formato YYYY-MM-DD => ')
    year, month, day=map(int, start.split('-'))
    start=dt.date(year, month, day)
    end=input('\tInserire la data di fine nel formato YYYY-MM-DD => ')
    year, month, day=map(int, end.split('-'))
    end=dt.date(year, month, day)

    while (not(lista.empty) and risposta=='Y'):

        print ('\nLista dei titoli non scaricati :\n')
        time.sleep(1)
        print (lista)      
        risposta=input('\nDesideri scaricare i titoli della lista (Y,N) ? ')
        risposta=risposta.upper()
    
        if risposta=='Y':
            df, lista=Load_tick(lista, start, end) # la funzione restituisce i valori dei titoli e la lista dei titoli ancora da scaricare
            shares=pd.concat([shares, df]) # I valori dei titoli scaricati vengono concatenati alla lista di quelli già scaricati in precedenza
          
        else:
            pass
            
        # Stampo l'elenco dei titoli che sono stati scaricati    
        print ('\n\n\n#### Ricerca terminata: ####')
        
        print ('\n\tIl DataFrame "shares" contiene ora i seguenti titoli:')       
        if not(shares.empty): # verifico che la lista dei titoli scaricati non sia vuota
            elenco=list(shares['Tick'].unique()) # lista dei tick scaricati
            for i in elenco:
                print ('\t', i)
        else:
            print('\t---')
        
        print('\n\tI seguenti titoli non sono stati scaricati:') # avviso l'ultente nel caso in cui non siano stati scaricati titol
        if lista.empty:
            print('\t---')
        else:
            for i in lista:
                print('\t', i)
    shares=shares.drop_duplicates()         # rimuove i duplicati, con Yahoo finance succede ...
    return shares

# Funzione che scarica da Yahoo un singolo titolo e lo aggiunge ad un elenco di titoli dinamico
def Load_ticker():
    """ Scarica da Yahoo un singolo ticker
    
    - La tenta un numero Max di volte di scaricare il dato da Yahoo per prevenire
      i frequenti casi nei quali il darto non e' disponibile al primo tentativo.
    - E' previsto un controllo per prevenire che venga richiesto di scaricare più di
      una volta il medesimo titolo.
    - Inserire END per terminare
    - Per tutti i titoli viene utilizzato il medesimo periodo storico (inizio e fine)    
    """
    
    shares=pd.DataFrame([]) #creo il df che conterrà i dati dei titoli che saranno via via richiesti dall'utente
    ticker_name='' #inizializzo il nome del ticker da scaricare
    # Input data di inizio e fine della serie storica
    start=input('Enter the START date in YYYY-MM-DD format => ')
    year, month, day=map(int, start.split('-'))
    start=dt.date(year, month, day)
    end=input('Enter the END date in YYYY-MM-DD format => ')
    year, month, day=map(int, end.split('-'))
    end=dt.date(year, month, day)
    while ticker_name!='END':
        disregard=False # Flag usato per evitare richieste duplicate per il medesimo tick    
        ticker_name =input ('Inserire un nuovo Tick da scaricare, END per terminare ==> ') #input dell'ID del titolo da scaricare
        ticker_name=ticker_name.upper()
        if not(shares.empty):
            if list(pd.DataFrame(shares.Tick.unique()).isin([ticker_name]).any())==[True]: # verifico se il tick è tra quelli già scaricati 
                print('\t\tTick già presente, non sarà ricaricato')
                disregard=True # se il titolo è già stato richiesto setto a True il flag disregard
        if (ticker_name!='END' and disregard==False):
            j=0 # contatore del numero dei tentativi fatti di scaricare il dato
            Max=3 # numero massimo di tentativi di download prima di chiedere nuova conferma all'utente
            df=pd.DataFrame([]) #dataframe nel quale mettero i dati sull'anadamento dei titoli  
            while (df.empty and j<Max):
                j+=1
                print ('\n')
                print ('\tScarico il tick (%i tentativo di %i): ' %(j, Max))
                try:
                    df=pdr.get_data_yahoo(ticker_name, start, end) # dati estratti da internet con Pandas_Datareader 
                    df['Tick']=ticker_name # aggiungo al df con i dati del titolo il ticker del titolo
                    print ('\t\t', ticker_name, ': OK, scaricato.') # confermo di avere scaricato il tick
                    shares=pd.concat([shares, df]) # Concateno il df_tick del tick che ho appena scaricato ai dati di tutti i tick scaricati fino ad ora        
                except:
                    print ('\t\t', ticker_name, ':NON scaricato, ritento') # nel caso in cui non abbia ricevuto dati dal server yahoo lascio il tick nella lista in modo da riprovare con il loop esterno ed avviso l'utente che non ho reperito il dato               
            if j> Max:
                print('\t\tNon sono riuscito a scaricare il titolo, richiederlo nuovamente per riprovare')
    print('\nIl DataFrame "shares" contiene ora i seguenti titoli:')
    if not(shares.empty): # verifico che la lista dei titoli scaricati non sia vuota in modo da prevenire errori run-time
        elenco=list(shares['Tick'].unique()) # lista dei tick scaricati
        for i in elenco:
            print ('\t', i)
    else:
        print('---')
    shares=shares.drop_duplicates()  # rimuove i duplicati ... succede
    return shares            

# seleziona un ticker dal DataFrame shares che contiene tutti i ticker scaricati e lo assegna ad un DataFrame con nome ticker
def Tick_dataframe(shares, tick_name):
    """ Crea un DataFrame di nome usuale al ticker del titolo selezionandoli dal DF di tutti i titoli che sono stati scaricati.
    Con le funzioni 1. e 2. del programma ho crato un Df di diversi titoli. Con questa funzione posso selezionarne uno solo e creare
    un DF con nome uguale a quello del ticker salvo la sostituzione del '.MI' con '-MI' """
    tick_name=tick_name.upper()
    df=shares[shares.Tick==tick_name]
    #df.index=df['Date']
    #del df['Date']
    
    tick_name=tick_name.replace('.', '_') # il titolo di Milano per yahoo termina con '.MI', quando nel main eseguo il comando Exec per assegnare il df al nome del ticker succede che PY pensa che '.MI' sia un metodo di ticker e si incasina. Allora sostituisco il '.' con '-'. Il df che otterrò sarà allora as esempio 'ENEL-MI' al posto di 'ENEL.MI', per ora è il meglio che mi è riuscito.   
    return df, tick_name
                
def save_file(shares):
    """ Salva il DataFrame delle azioni nei formati Excel File, CSV, TXT.    
    Il DataFrame Shares dei titoli viene salvato come file XLS nella directory di lavoro definita nella variabile path"""
    
    # enter nome del file in cui salvare i dati, senza estensione
    nome_file=input('\n\tNome del file da utilizzare per salvare i dati (senza estensione) : ')
    xls_file=path+nome_file+'.xls'
    csv_file=path+nome_file+'.csv'
    txt_file=path+nome_file+'.txt' 
    print ('\n\tSalvo il DataFrame "Shares" delle azioni nel file Shares')
    print ('\tI files vengono salvati nel folder: ', path)    
    #Salvo file in formato excel     
    if len(shares)<65536:    # se il file è più lungo del formato massimo accettabile da xls non salvo ed avviso l'utente. Diversamente andrebbe in crash
        shares.to_excel(xls_file)
        print('\tI dati sono stati salvati in formato xls nel file ', xls_file)
    else:
        print('\n\tIl file contiene ', len(shares), ' righe, è troppo grande per Excel. Verrà salvato solo come testo.')
    #Salvo file in formato csv    
    shares.to_csv(csv_file, sep=',', na_rep='', )
    print('\tI dati sono stati salvati in formato csv nel file ', csv_file)
    #Converto il file da formato csv in txt e lo salvo
    with open(txt_file, "w") as my_output_file:
        with open(csv_file, "r") as my_input_file:
            [ my_output_file.write(" ".join(row)+'\n') for row in csv.reader(my_input_file)]
    my_output_file.close()
    print('\tI dati sono stati salvati in formato txt nel file ', txt_file)
    
def load_file():
    """ Legge un file di titoli in formato CVS e lo assegna al df share 
    """    
    print ('\n\tCarica un file nel DataFrame di nome "df"')
    print ('\tIl file dei dati deve essere in formato CSV, virgola come separatore, punto per i numeri decimali')
    print ('\tIl file viene letto dal folder di nome ', path)
    file_name=input('\n\t\tNome del file che contiene i dati (includere la estensione .CSV) ==>')
    csv_file=path+file_name
    df=pd.read_csv(csv_file)
    
    df.index=df['Date']
    del df['Date']
       
    
    print('\tI dati sono stati caricati nel DataFrame di nome "df"')
    return df

def stat(shares):
    """ Calcola alcune statistiche di utilizzo comune per tutto l'intervallo tra la data iniziale e quella finale
    
    - da principio raggruppo il df shares dei titoli per Tick
    - quindi calcolo la statistica di interesse
    - infine concateno la statistica di interesse nel df di uscita della funzione
    """
    print('\n\tCalcola statistiche per il df shares')
    cosa=input('\t\tDato per il quale di desidera calcolare la statistica (Close, Adj Close, Volume, ...)==>') # parametro per il quale calsolare la statistica
    out=pd.DataFrame([])   #df che conterrà il df di uscita dalla funzione al main
    calcolo=pd.DataFrame([]) #df per il calcolo dei subtotali  
    result=pd.DataFrame([]) #df con l'ultimo dato disponibile   
    group=shares.groupby('Tick')[cosa] #conto quanti dati ho per ciascun ti<ck per il calcolo della statistica
    calcolo=group.count()
    out=calcolo    
    lista=shares.Tick.unique() #qui ricavo l'ultimo dato disponibile per il parametro che sto analizzando
    for i in lista: #per ciascun titolo nella lista dei titoli prendo l'ultimo dato e la sua data e la metto nel df di uscita
       fd=shares[shares.Tick==i].sort_index().tail(1)  
       result=result.append(fd)
    result['Date']=result.index   
    result.index=result['Tick'] # assecgno tick ad indice di result per potere fare append con out
    del result['Tick'] # cancello la colonna tick di result per evitare duplicazioni
    out=pd.concat([out,result[cosa], result['Date']], axis=1) # concateno result con out, questa operazione non funzionerebbe in modo corretto se tick non fosse indice di result
    calcolo=group.max() # Calcolo del massimo per ciascun ticl 
    out=pd.concat([out,calcolo], axis=1)
    calcolo=group.min() # calcolo del minimo
    out=pd.concat([out,calcolo], axis=1)
    calcolo=group.max()-group.min() # range tra max e min per ciascun tick
    out=pd.concat([out,calcolo], axis=1)    
    calcolo=(group.max()-group.min())/group.min() # rapporto tra range e min
    out=pd.concat([out,calcolo], axis=1)    
    calcolo=group.mean() # media   
    out=pd.concat([out,calcolo], axis=1)
    calcolo=group.std() # dev standard   
    out=pd.concat([out,calcolo], axis=1)
    calcolo=group.std()/group.mean() # rapporto tra dev std e media
    out=pd.concat([out,calcolo], axis=1)
    calcolo=group.skew() # skewness
    out=pd.concat([out,calcolo], axis=1) 
    calcolo=group.apply(pd.DataFrame.kurt) #kurtosis
    out=pd.concat([out,calcolo], axis=1)
    out.columns=['Nr', cosa, cosa + ' last_date', 'max','min', 'range', 'range on min', 'mean', 'std', 'std on mean', 'skewness', 'kurtosis']
    return out    

def correlation(shares):
    """ Correlazione tra prezzo e volume di un medesimo titolo
    
    Riceve in ingresso il df 'shares' con i prezzi delle azioni
    calcola la correlazione e disegna la heat map
    """


    print('    Calcola il coefficiente di correlazione tra i titoli del df "shares":\n')
    print('    Tick \ Numero dei dati')
    format = lambda x: '%.2f' %x
    lista=shares.Tick.sort_values().unique() #lista dei tick per iquali verra eseguito il calcolo della correlazione
    for i in lista: #stampo l'elenco dei titoli
        print('        ',i, '\\' , len(shares.Tick[shares.Tick==i]))    
    risposta=input('\n\t\tVuoi procedere con il calcolo dei coeff. di correlazione (Y/N)? ==>')
    if risposta.upper()!='Y':
        print ("\n\tCalcolo NON eseguito come da richiesta dell'utente")
    else:
        # Esistono titoli per i quali molti dati non sono disponibili, ad esempio perchè recentemente immessi in borsa
        # dovrei toglierli dalla lista dei titoli da analizzare se manca più del 5% del totale
        risposta1=input('\n\tPer che dato è richiesto il calcolo (Close, Adj Close, Volume, Open, High, Low)? ==>')
        d=pd.DataFrame(index=lista,columns=lista) #creo un df quadrato con i nomi delle righe e delle colonne uguali a quelli dei Tick, verra' popolato con i coefficienti di correlazion
        for i in lista: # itero la tabe3lla con i ticker delle azioni sulle right e sulle colonne
            for j in lista:
                c= shares[risposta1][df.Tick==i].corr(shares[risposta1][df.Tick==j]) # calcolo coeff di correlazione, da vedere se si riesce ad evitare il loop e sostituire con operazione a livello di df
                d.loc[i,j]=c  # assegno ad una cella il valore del coeff. di correlazione che ho calcolato tra due titoli     
        d1=d.fillna(0) #la mappa va' in crash quando corr e NaN, da perfezionare con mascheratura di NaN lavorando sul df 'd' al posto di 'd1'
        # Generate a mask for the upper triangle      Serve per tagliare i dati simmetrici nella tabella mettendo poi mask=mask nella heatmap sotto, però la voglio vedere tutta, quili metto queste linee come remark
        #mask = np.zeros_like(d1, dtype=np.bool)
        #mask[np.triu_indices_from(mask)] = True        
        d1.applymap(format)
        try:
            print('\nRispetto al FTSEMIB i coeff. di correlazione di "%s" sono i seguenti:\n' %risposta1)
            print(d1.loc[:,'FTSEMIB.MI'].sort_values(ascending=False))
        except:
            pass
        fig, ax = plt.subplots(figsize=(15,15))         # figsize in inches, used to define the dimensions of the heatmap ia line below
        sns.heatmap(d1, square=True, linewidths=.5, cmap=sns.diverging_palette(240, 10, n=11), cbar_kws={"shrink": 0.8}, ax=ax) # costruzione della mappa dei coeff di correlazione con seaborn  d1 : è il df dei coeff di correlazione calcolata sopra // square=True impogo che le caselle della heatmap siano quadrate e non rettangolari  // linewidths=.5  questo è lo spazio tra una cella e quella adiacente // cmap=sns.diverging_palette(240, 10, n=11) questa è la mappa dei colori //  cbar_kws={"shrink": 0.8} dimensioni in altezza della barra laterale con la legenda 0.8 = 80%  // ax=ax  questa è la dimensione in pollici della heatmap
        print('\nEcco la heatmap dei coefficienti di correlazione:')        
        plt.show() # used to print the plt during the execution of the program, without this instruction the plt is printed only at the end of the program execution
        
        risposta=input('Ti interessa qualche correlazione in particolare (Y/N)? ==>')
        if risposta.upper()!='Y': #verifico che l'utente voglia eseguire il lungo calcolo dei cofficienti di correlazione
            print ("\n\tCalcolo NON eseguito come da richiesta dell'utente")
        else:
            lista=list([])
            ticker_name =input('Inserire un nuovo Ticker per il quale mostrare la correlazione, END per terminare ==> ') #input dell'ID del titolo da scaricare
            while ticker_name.upper()!='END':
                lista.append(ticker_name.upper())
                ticker_name =input ('Inserire un nuovo Tick da studiare, END per terminare ==> ') #input dell'ID del titolo da scaricare
            print('\n')
            if len(lista)==1:
                for i in lista:
                    print('Correlazione di %s con gli altri titoli' %i)
                    print(d1.loc[:,i].sort_values(ascending=False))
                    print('=========================\n')
            elif len(lista)>1:
                for i in lista:
                    print('Correlazione di %s con gli altri titoli' %i)
                    print(d1.loc[lista,i].sort_values(ascending=False))
                    print('=========================\n')                
            
        print('\nIl df con il risultato della correlazione si trova in df_corr per le successive analisi.\n')
        return d1

def grafico(shares):
    """ Disegna il grafico di un titolo
 
    """

    d=shares.Close[shares.Tick=='FTSEMIB.MI']
    d.plot(figsize=(16,12)).show()
    #plt.show()

def df_traderlink():
    print('\nAssegna al DF "df_tdl" il contenuto della tabella internet Traderlink con la performance di mercato')
    print('la tabella deve avere le colonne Titolo, Prezzo, Var%, Ora, Denaro, Qtà, Lettera, Qtà, N.Contr')
    url=input('\nInserire URL da convertire in df ==>')
    lista=pd.read_html(url, thousands='.', decimal=',') #leggo url come html che diventa una lista di due liste
    lista=lista[0] # la prima lista contiene i dati di borza, la seccona contiene dati che non interessano e che butto
    righe=len(lista) # questo è il numero delle righe del futuro df
    colonne=int(lista.size/righe) # queste sono le colonne del df, dovrebbero essere sempre 9, cioè la dimensione della lista diviso per il numero delle righe
    freccia=np.array(lista).reshape(righe,colonne) #converto la lista in array numpy per potere applicare rashape in modo da farlo poi diventare un df
    df=pd.DataFrame(freccia) # converto array in df
    df.columns=df.iloc[0,:] # la ridha zero della tabella traderlink contiene i titoli delle colonne
    df=df.drop(0) #elimino la riga zero che non mi occorre piu
    df['Index']=range(0,len(df))
    df.index=df['Index']
    del df['Index']
    df.columns=['Tick', 'Price', 'Var', 'Time', 'PB', 'QB', 'PS', 'QS','Nr Ctr']     #rinomino le colonne perche i nomi di traderlionk non mi piacciono (duplicazioni, accenti etc)
    df.index=df['Tick']
    del df['Tick']
    df['Var']=[x.replace(',', '.') for x in df['Var']]
    df['Var']=[x.replace('%', '') for x in df['Var']]
    df['Var']=df['Var'].astype(float)
    df['Time'].astype(dt.time)
    lista=df.columns
    lista=lista.drop(['Var','Time'])
    df[lista]=df[lista].astype(float)    
    df['Spread']=df['PS']-df['PB']      
    df['Spread pct']=df['Spread']/df['Price']   
    df['Dim']=(df['PB']*df['QB']+df['PS']*df['QS'])/df['Nr Ctr']
    #format=lambda x: '%.2f' %x        
    #df['Buy']=df['Buy'].astype(float).applymap(format)          
    return df
      
                  
# Main
""" Main si limita a chiedere all'utente quali funzioni del programma desidera eseguire

    Il principio ispiratore e' quello di fornire alcune operazioni di base ripetitive
    lasciando comunque allo shell la analisi dei dati.
    Per questo motivo i dati elaborati dal programma restano in memoria in modo che i risultati siano
    disponibili in shell

"""    

risposta='0'
while risposta !='99':
    print ('\n\n##### Elenco funzioni disponibili #####\n\n')
    print ('\t1.', fg.YELLOW, style.BRIGHT, 'SCARICA da YAHOO', style.RESET_ALL, 'la lista dei titoli nel file Tick_list.xls e la assegna al df "shares"')
    print ('\t2', fg.RED, style.BRIGHT, ' SCARICA UN SINGOLO', style.RESET_ALL, 'ticker da Yahoo e lo aggiunge al DataFrame "shares"')
    print ('\t3.', fg.BLUE, style.BRIGHT,'ASSEGNA TUTTI', style.RESET_ALL,'i tick da "shares" a DataFrames col nome del tick')   
    print ('\t4.', fg.MAGENTA, style.BRIGHT,'ASSEGNA UN SINGOLO', style.RESET_ALL, 'tick da "shares a un DataFrame col nome del tick')
    print ('\t5.', fg.GREEN, style.BRIGHT, 'SALVA TUTTI', style.RESET_ALL,'i titoli nei formati xls, csv e txt')
    print ('\t6.', fg.YELLOW, style.BRIGHT, 'LEGGE', style.RESET_ALL,'un file di titoli in formato CSV e lo assegna al DataFrame di nome "df"')    
    print ('\t7.', fg.RED, style.BRIGHT, 'STATISTICHE', style.RESET_ALL,'descrittive, vengono assegnate al df "stat"')
    print ('\t8.', fg.BLUE, style.BRIGHT, 'CORRELAZIONE', style.RESET_ALL ,'tra titoli del listino')       
    print ('\t9. -- TEST PLOT grafico --')
    print ('\t10.', fg.GREEN, style.BRIGHT, 'Df con dati Traderlink', style.RESET_ALL,'assegnato a df_tdl')    
    print ('\t99. FINE')
    risposta=input('\n ==> ')
    # Scarica da internet le azioni richieste dal file Tick_list
    if risposta=='1':
        shares=Load_listino()
    # Scarica un singolo Tick richiesto dall'utente da tastiera
    if risposta=='2':    
        shares=Load_ticker()
    # Spacchetta tutti i tick del DataFrame shares in singoli dataframe con nome uguale al tick
    if risposta =='3':
        tick_list=shares.Tick.unique()
        for tick_name in tick_list:
            df, tick_name=Tick_dataframe(shares, tick_name) #passo alla funzione Tick_dataframe la lista di tutti i titoli che ho scaricato, la funzione mi restituisce il df del solo titolo selezionato ed il nome del tick che utilizzerò per creare il dataframe con il nome del titolo
            exec(tick_name+"= df") # creo una variabile di nome uguale al contenuto di tick_name la quale contiene il df con il solo titolo selezionato dalla funzione Tick_dataframe, uso la funzione exec perchè è un indiretto.
            print ('\tHo creato il DataFrame di nome "%s"' %tick_name)
        print ('\nOperazione completata')
    # Assegna uno dei tick del DataFrame shares ad un DataFrame di nome uguale a quello del tick
    if risposta =='4':
        tick_name=input('\tTick del titolo ==> ')
        df, tick_name=Tick_dataframe(shares, tick_name) #passo alla funzione Tick_dataframe la lista di tutti i titoli che ho scaricato, la funzione mi restituisce il df del solo titolo selezionato ed il nome del tick che utilizzerò per creare il dataframe con il nome del titolo
        exec(tick_name+"= df") # creo una variabile di nome uguale al contenuto di tick_name la quale contiene il df con il solo titolo selezionato dalla funzione Tick_dataframe, uso la funzione exec perchè è un indiretto.
        print ('\tHo creato il DataFrame di nome "%s"' %tick_name)        
    # Salva tutto il DataFrame delle azioni in un file excel
    if risposta =='5':
        save_file(shares)
        #except:
        #    print('\n\tSalvataggio non riuscito.')
    # Carica un file in un df
    if risposta =='6':
        df=load_file()
        risposta_1=input('\n\t\tVuoi assegnare "df" al dataframe "shares" con i dati delle azioni (Y/N)? ==>')
        if risposta_1.upper()=='Y':
            shares=df
        else:
            print('\tAssegna manualmente da shell "df" al dataframe che desideri')
    # Calcola un df di statistiche comuni    
    if risposta =='7':
        stat=stat(shares)
        print('\n\t Ecco il df "stat" delle statistiche :\n\n', stat)
        risposta_1=input('\n\tVuoi salvare il df come file (Y/N)? ==>')
        if risposta_1.upper()=='Y':
            save_file(stat)
        else:
            print('\n\tFile non salvato, il risultato resta disponibile nel df "stat"')
    if risposta =='8':
        df_corr=correlation(shares)
    if risposta =='9':
        grafico(shares) 
    # Termina la esecuzione del programma
    if risposta =='10':
        df_tdl=df_traderlink()
        print("\nEcco il 'df_tdl' con l'andamento attuale del mercato:\n")
        print(df_tdl.to_string())
    # Termina la esecuzione del programma
    else:
        pass
    if risposta=='99':
        print('\n\tProgramma terminato come richiesto.')
    
