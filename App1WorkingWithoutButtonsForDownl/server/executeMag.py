import numpy as np
import pandas as pd
import sys

def is_kod(stroka):
    otv=False
    for elem in stroka:
        if ('0'<=elem<='9'):
            otv=True
            break
    proverka=stroka.find('ООО')
    if (proverka != -1):
        otv=False
    return otv


def combine_identical_providers(table):
    otv=pd.DataFrame()
    for i,naimenovanie in enumerate(table['Наименование'].unique()):
        tekdata=table[table['Наименование']==naimenovanie]
        #print(tekdata.shape)
        for j,postavchik in enumerate(tekdata['Поставщик'].unique()):
            #print(naimenovanie,postavchik)
            tekd=tekdata[tekdata['Поставщик']==postavchik]
            #print(tekd.shape)
            #print(list(tekd.iloc[:,2]))
            
            
            mas_of_tup=[]
            for price in tekd.iloc[:,3].unique():
                td=tekd[tekd[tekd.columns.values[3]]==price]
                first_date=list(td.iloc[:,2])[0]
                last_date=list(td.iloc[:,2])[-1]
                if(price!='Missing'):
                    mas_of_tup.append(tuple([price,first_date,last_date]))
                else:
                    mas_of_tup.append(tuple([0,first_date,last_date]))
               
            #print(mas_of_tup)
            #mas_of_tup.sort()
            mas1=mas_of_tup.copy()
            mas2=mas_of_tup.copy()
            mas1.sort(key=lambda x: str(x[2][6:8])+str('.')+str(x[2][3:5])+str('.')+str(x[2][0:2]))
            mas2.sort(key=lambda x: x[0])
            #print(mas1)
            #print(mas2)
            if (mas1[-1]!=mas2[-1]):
                tup=tuple([mas1[-1],mas2[-1]])
            else:
                tup=tuple([mas1[-1]])
            #print(tup)
            
            
            tekotv=pd.DataFrame({tekd.columns[0]:[naimenovanie],tekd.columns[1]:[postavchik],tekd.columns[3]:[tup]})
            #print(tekotv)
            if (i==j==0):
                otv=tekotv
            else:
                otv=otv.append(tekotv)
    return otv


def create_one_number_from_providers(table):
    otv=pd.DataFrame()
    names=table['Наименование'].unique()
    names.sort()
    for i,naimenovanie in enumerate(names):
            tekdata=table[table['Наименование']==naimenovanie]
            #print(tekdata.shape)
            def f(x):
                #print(x)
                if(x=='---'):
                    return 0
                if len(x)==1:
                    return x[0][0]
                else:
                    return 0.5*(x[0][0]+x[1][0])
                
            mas=[f(x)  for x in tekdata.iloc[:,2] ]
            #mas=[x[0]  for y in tekdata.iloc[:,2]  for x in y]
            mas=np.array(mas)
            #print(mas)
            sredn=mas.mean()
            if (sredn!=0):
                mask=(mas!=0)
                #print(mask)
                N=len(mas[mask])
                sredn=mas.sum()/N
            tekotv=pd.DataFrame({tekdata.columns[0]:[naimenovanie],tekdata.columns[2]:[sredn]})
            #print(tekotv)
            for j in range(3,tekdata.shape[1]):
                mas=[f(x)  for x in tekdata.iloc[:,j] ]
                mas=np.array(mas)
                sredn=mas.mean()
                if (sredn!=0):
                    mask=(mas!=0)
                    N=len(mas[mask])
                    sredn=mas.sum()/N
                tekotv[tekdata.columns[j]]=sredn
            if (i==0):
                otv=tekotv
            else:
                otv=otv.append(tekotv)
    return otv




def get_one_table(fin):
    Df=pd.read_excel(fin)
    Df.fillna('Missing',inplace=True)
    Df=Df[Df[Df.columns[0]]!='Missing']
    mas_of_j=[]
    for j in range(Df.shape[1]):
        #print ("j=",j,"len=",len(Df.iloc[:,j].unique()))
        if (j==1 or j==5 or len(Df.iloc[:,j].unique())>3):
            mas_of_j.append(j)
    #print(mas_of_j)
    Df=Df.iloc[:,mas_of_j]
    
    #Df.to_excel('Test3.xlsx',index=True)
    
    Df.columns=['Поставщик','Код', 'Наименование','Цена', 'Кол-во','Цена б/н', 'Цена в/н','Сумма б/н','НДС','Сумма в/н']
    Df=Df[~Df['Поставщик'].isin(['Группировка по корреспондентам','Корреспондент','Итого по группе'])]
    
    #Df.to_excel('Test4.xlsx',index=True)
    
    tek_kod=Df.iloc[0][0]
    tek_naimenovanie=Df.iloc[0][2]
    for i in range(Df.shape[0]):
        if (is_kod(Df.iloc[i][0])==True):
            tek_kod=Df.iloc[i][0]
            tek_naimenovanie=Df.iloc[i][2]
        elif (is_kod(Df.iloc[i][0])==False):
            Df.iloc[i][1]=tek_kod
            Df.iloc[i][2]=tek_naimenovanie
    Df=Df[Df['Код']!='Missing']
    
    #Df.to_excel('Test5.xlsx',index=True)
    
    mas_of_tuples=[]
    for naimenovanie in Df['Наименование'].unique():
        tekDf=Df[Df['Наименование']==naimenovanie]
        for i in range(tekDf.shape[0]):
            mas_of_tuples.append((naimenovanie,tekDf.iloc[i][0]))
    #print(mas_of_tuples)
    my_index=pd.MultiIndex.from_tuples(mas_of_tuples,names=['Наименование','Поставщик'])
    otv=pd.DataFrame(Df.iloc[:,[3,6]].values,index=my_index,columns=[str('Date'),fin])
    #otv.to_excel('Test1.xlsx',index=True)
  
    
    #otv.drop_duplicates(inplace=True)
    
    #otv.to_excel('Test2.xlsx',index=True)
    
    otv.reset_index(inplace=True)
    
    
    
    for i in range(otv.shape[0]):
        otv.iloc[i,0]=otv.iloc[i,0].upper()
    for i in range(otv.shape[0]):
        otv.iloc[i,1]=otv.iloc[i,1].upper()
        
    for i in range(otv.shape[0]):
        otv.iloc[i,1]=otv.iloc[i,1].replace('ООО','')
        otv.iloc[i,1]=otv.iloc[i,1].replace('ТД','')
        otv.iloc[i,1]=otv.iloc[i,1].replace('ИП','')
        otv.iloc[i,1]=otv.iloc[i,1].replace(' ','')
        otv.iloc[i,1]=otv.iloc[i,1].replace('\n','')
        otv.iloc[i,1]=otv.iloc[i,1].replace('\"','')
        otv.iloc[i,1]=otv.iloc[i,1].replace('.','')
        
    otv=combine_identical_providers(otv)
    
    return otv

def count_union(table1,table2):
    set1=set(table1['Наименование'])
    set2=set(table2['Наименование'])
    set3=set1.union(set2)
    print(len(set1),len(set2),len(set3))
    
    
def unite_tables(table1,table2):
    set1=set(table1['Наименование'])
    set2=set(table2['Наименование'])
    set3=set1.union(set2)
    print(len(set1),len(set2),len(set3))
    mas_of_index=[]
    mas_vstack=[]
    
    list4=list(set3)
    list4.sort()
    #print(list4)
    #list4=[]
    #for name in table1['Наименование'].unique():
        #if name in set3:
           # list4.append(name)
    #print(len(list4))
    for i,naimenovanie in enumerate(list4):
        
        tekt1=table1[table1['Наименование']==naimenovanie].drop('Наименование',axis=1)
        tekt2=table2[table2['Наименование']==naimenovanie].iloc[:,[1,2]]
        #print(naimenovanie,len(tekt1),len(tekt2))
        
        if (naimenovanie in set1):
            tekotv=pd.merge(tekt1,tekt2,on='Поставщик',how='outer')
        else:
            tekotv=pd.merge(tekt2,tekt1,on='Поставщик',how='outer')
        
        
        #print(tekotv.shape[0])
        for j in range(tekotv.shape[0]):
            mas_of_index.append(naimenovanie)
        if (i==0):
            mas_vstack=tekotv
        else:
            mas_vstack=mas_vstack.append(tekotv)
            
    #print(tekotv)
            
    OTV=pd.DataFrame(mas_of_index)
    for i in range(mas_vstack.shape[1]):
        OTV[mas_vstack.columns[i]]=list(mas_vstack.iloc[:,i].values)
    OTV.fillna('---',inplace=True)
    #OTV.columns=['Наименование','Поставщик', 'TableMagadanPresna.xlsx', 'TableStrana.xlsx'] if case 1
    #OTV.columns=['Наименование', 'TableMagadanPresna.xlsx', 'TableStrana.xlsx','Поставщик'] if case 2
    #mas_of_columns_names=['Наименование']
    #for i,name in enumerate(list(OTV.columns)):
        #if (i!=0):
            #mas_of_columns_names.append(name)
    mydict={0:'Наименование'}
    for name in OTV.columns.values[1:]:
        mydict.update({name:name})
    OTV.rename(columns=mydict,inplace=True)
    if (OTV.columns.values[-1]=='Поставщик'):
        new_mas=['Наименование','Поставщик']
        for name in OTV.columns.values:
            if (name!='Поставщик' and name!='Наименование'):
                new_mas.append(name)
        OTV=OTV[new_mas]
    #print(mas_of_columns_names)
    #OTV.columns=mas_of_columns_names
    #print(OTV)
    return OTV
    
    
def heap_tables(list_of_restaurants):
    Table_otv=get_one_table(list_of_restaurants[0])
    for i in range(1,len(list_of_restaurants)):
        tek_table=get_one_table(list_of_restaurants[i])
        Table_otv=unite_tables(Table_otv,tek_table)
    return Table_otv

def make_index_for_table(Table_otv):
    mas_of_tuples=[]
    names=Table_otv['Наименование'].unique()
    names.sort()
    for naimenovanie in names:
        tekDf=Table_otv[Table_otv['Наименование']==naimenovanie]
        for i in range(tekDf.shape[0]):
            mas_of_tuples.append((naimenovanie,tekDf.iloc[i][1]))
    my_index=pd.MultiIndex.from_tuples(mas_of_tuples,names=['Наименование','Поставщик'])
    otv=Table_otv.drop(['Наименование','Поставщик'],axis=1)
    otv=otv.set_index(my_index)
    return otv
    
def get_otchet_Both(list_of_restaurants):
    Table_otv=heap_tables(list_of_restaurants)
    otv=make_index_for_table(Table_otv)
    otv.to_excel('OtchetWithProviders.xlsx',index=True)
    Table_otv.head(5)
    otvOneNumber=create_one_number_from_providers(Table_otv)
    otvOneNumber.to_excel('OtchetOneNumber.xlsx',index=False)
    
    

    
list_of_restaurants1=['TableMagadanPresnaFood.xls',
                     'TableMagKrOktyabrFood.xls',
                     'TableMagadanBPFood.xls',
                     'TableStranaFood.xls',
                     'TableValenokFood.xls',
                     'TableFumisavaFood.xls']
list_of_restaurants2=['TableMagadanPresnaHoz.xls',
                     'TableMagKrOkyabrHoz.xls',
                     'TableMagadanBPHoz.xls',
                     'TableStranaHoz.xls',
                     'TableValenokHoz.xls',
                     'TableFumisavaHoz.xls']

list_of_rest=[]
for i in range(1,len(sys.argv)):
    list_of_rest.append(sys.argv[i])

#%time
get_otchet_Both(list_of_rest)
#%time get_otchet_OneNumber(list_of_restaurants1[0:2])

#Table_otv=heap_tables(list_of_restaurants1)
#otv=make_index_for_table(Table_otv)
#otv.to_excel('OtchetWithProviders.xlsx',index=True)
#Table_otv.head(5)
