#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import networkx as nx
import random


# In[ ]:


df_inputs = pd.read_csv('inputs.csv')
df_outputs = pd.read_csv('outputs.csv')
df_transactions = pd.read_csv('transactions.csv')


# In[ ]:


class Transazione:
    def __init__(self,id_trans,block_id,tot_input,tot_output):
        self.id_trans = id_trans
        self.block_id = block_id
        self.tot_input = tot_input
        self.tot_output = tot_output
        self.coinbase = False
        self.is_valid = True
        self.output = []
        self.input = []
    
    def printTx(self):
        print('id tx ' + str(self.id_trans),'block id ' + str(self.block_id),'tot input ' + str(self.tot_input),'tot output ' + str(self.tot_output), 'coinbase: ' + str(self.coinbase), 'tx valida: ' + str(self.is_valid))
    
    def delTx(self):
        self.id_trans = 0
        self.block_id = 0
        self.tot_input = 0
        self.tot_output = 0
        self.coinbase = False
        self.is_valid = True

class OutputTx:
    def __init__(self,id_output,is_valid):
        self.id_output = id_output
        self.is_valid = is_valid
        
class InputTx:
    def __init__(self,id_input,is_valid):
        self.id_input = id_input
        self.is_valid = is_valid
        
        
class Input:
    def __init__(self,id_input,id_trans,sig_id,output_id):
        self.id_input = id_input
        self.id_trans = id_trans
        self.sig_id = sig_id
        self.output_id = output_id
        self.is_valid = True
        self.is_double = False
        
    def printInp(self):
        print('id input ' + str(self.id_trans),'id tx ' + str(self.id_trans),'sig_id ' + str(self.sig_id),'output id ' + str(self.output_id),'valido ' +str(self.is_valid) )

class Output:
    def __init__(self,id_output,id_trans,pk_id,value):
        self.id_output = id_output
        self.id_trans = id_trans
        self.pk_id = pk_id
        self.value = value
        self.is_valid = True
        self.is_utxo = True
        self.is_spent = 0
    
    def printOut(self):
        print('id output ' + str(self.id_output),'id tx ' + str(self.id_trans),'pk_id ' + str(self.pk_id),'value ' + str(self.value),'valida '+ str(self.is_valid))


# In[ ]:


#transazioni
tx_array = []
for index_trans in df_transactions.index:
    id_transazione_attuale = df_transactions['id'][index_trans]
    block_id_transazione_attuale = df_transactions['block_id'][index_trans]
    tx_array.append(Transazione(id_transazione_attuale,block_id_transazione_attuale,0,0))
    
#output
output_array = []

for index_output in df_outputs.index:
    id_out = df_outputs['id'][index_output]
    id_tx = df_outputs['tx_id'][index_output]
    pk_id = df_outputs['pk_id'][index_output]
    value = df_outputs['value'][index_output]
    output_array.append(Output(id_out,id_tx,pk_id,value))

input_array = []

#input
for index_input in df_inputs.index:
    id_in = df_inputs['id'][index_input]
    id_tx = df_inputs['tx_id'][index_input]
    sig_id = df_inputs['sig_id'][index_input]
    out_id = df_inputs['output_id'][index_input]
    input_array.append(Input(id_in,id_tx,sig_id,out_id))


# In[ ]:


#per ogni tx, aggiorno la lista degli input e output per quella tx
for index,out in enumerate(output_array):
    tx_array[out.id_trans-1].output.append(OutputTx(out.id_output,0))
    
for index,inp in enumerate(input_array):
    tx_array[inp.id_trans-1].input.append(InputTx(inp.id_input,0))


# In[ ]:


#transazioni coinbase valide e non valide

for index, inp in enumerate(input_array):
    if inp.sig_id == 0 and inp.output_id == -1:
        tx_array[inp.id_trans-1].coinbase = True

for index, out in enumerate(output_array):
    if tx_array[out.id_trans-1].coinbase:
           tx_array[out.id_trans-1].tot_output += out.value #ricompensa coinbase

k=0
for index,tx in enumerate(tx_array):
    if tx.coinbase == True:
        if  tx.tot_output != 5000000000 :
            tx.is_valid = False
            k+=1

print('Totale transazioni coinbase non valide: ' + str(k))


# In[ ]:


#calcolo tot degli output
for index,out in enumerate(output_array):
    if tx_array[out.id_trans-1].coinbase == False:
        tx_array[out.id_trans-1].tot_output += out.value


# In[ ]:


#controllo output negativi
for index,out in enumerate(output_array):
    if out.value < 0:
        out.is_valid = False
        tx_array[out.id_trans-1].is_valid = False


# In[ ]:


#calcolo tot degli input
#output_array.sort(key=lambda x: x.id_output)
for index,inp in enumerate(input_array):
     if tx_array[inp.id_trans-1].coinbase == False:
        if inp.output_id == 265834: #anomalo
            continue
        tx_array[inp.id_trans-1].tot_input += output_array[inp.output_id-1].value


# In[ ]:


#transazioni non valide per via di input < output
i=0
tx_array[15698].is_valid=False
for index,tx in enumerate(tx_array):
    if tx.coinbase == False:
        if tx.tot_input < tx.tot_output:
            tx.is_valid = False
            tx.printTx()
            i+=1
print('Tot transazioni non valide: ' + str(i))


# In[ ]:


#controllo firme
i=0
for index,inp in enumerate(input_array):
    if inp.output_id == 265834: #anomalo
        continue
    if inp.output_id == -1 :
        continue
    if inp.sig_id == -1 :
        continue
    if inp.sig_id == 0 :
        continue
    sign = output_array[inp.output_id-1].pk_id
    if sign == -1 :
        continue
    if sign != inp.sig_id:
        print(sign,inp.sig_id)
        i+=1
        tx_array[inp.id_trans-1].is_valid = False
print('Tot firme non valide: ' + str(i))


# In[ ]:


#output_array.sort(key=lambda x: x.id_output)
i=0
for index,inp in enumerate(input_array):
    if inp.output_id == 265834: #anomalo
        continue
    if inp.output_id == -1 :
        continue
    output_array[inp.output_id-1].is_spent +=1
    if output_array[inp.output_id-1].is_spent >1:
        inp.is_double = True
        i+=1
        inp.is_valid = False
        tx_array[inp.id_trans-1].is_valid = False
        inp.printInp()
        

print('Tot double spending: ' + str(i))


# In[ ]:


#invalid tx
invalid_tx_id = []
for index,tx in enumerate(tx_array):
    if tx.is_valid == False:
        invalid_tx_id.append(tx.id_trans)

print('Numero di tx non valide' + str(len(invalid_tx_id)))


# In[ ]:


for index,tx in enumerate(tx_array):
    if tx.is_valid == False:
        for index1,inp in enumerate(tx.input):
            input_array[inp.id_input-1].is_valid = False
        for index2,out in enumerate(tx.output):
            output_array[out.id_output-1].is_valid = False


# In[ ]:


i=0
for index,inp in enumerate(input_array):
    if inp.output_id == 265834: #anomalo
        continue
    if inp.output_id == -1 :
        continue
    #controllo se riferisce output di tx non valida
    if tx_array[output_array[inp.output_id-1].id_trans-1].is_valid == False:
        output_array[inp.output_id-1].is_valid = False #setto anche output come non valido
        for index3,out1 in enumerate(tx_array[output_array[inp.output_id-1].id_trans-1].output):
            output_array[out1.id_output-1].is_valid = False
        inp.is_valid = False #setto lo stesso input come non valido
        tx_array[inp.id_trans-1].is_valid = False #la transazione che sfrutta input derivato da output non valido, sarà invalidata
        for index2,out in enumerate(tx_array[inp.id_trans-1].output):
            output_array[out.id_output-1].is_valid = False
            #print( output_array[out.id_output].id_output,output_array[out.id_output].is_valid)
        if inp.id_trans not in invalid_tx_id:
            invalid_tx_id.append(inp.id_trans)
            i+=1

print('Transazioni non valide con meccanismo a catena: ' + str(i))

print('Totale transazioni non valide: ' + str(len(invalid_tx_id)))


# In[ ]:


#set all input and output for invalid tx as not valid
for index,tx in enumerate(tx_array):
    if tx.is_valid == False:
        for index1,inp in enumerate(tx.input):
            input_array[inp.id_input-1].is_valid = False
        for index2,out in enumerate(tx.output):
            output_array[out.id_output-1].is_valid = False


# In[ ]:


input_dict = {}
for index,inp in enumerate(input_array):
    if inp.is_valid:
        input_dict[inp.id_input] = (inp.id_trans,inp.sig_id,inp.output_id)

output_dict = {}
for index,out in enumerate(output_array):
    if out.is_valid:
        output_dict[out.id_output] = (out.id_trans,out.pk_id,out.value,0)
        

tx_dict = {}
for index,tx in enumerate(tx_array):
    if tx.is_valid:
        tx_dict[tx.id_trans] = (tx.block_id,0) #id,tot_utxo


# In[ ]:


#calcolo totale del valore di UTXO nel sistema
for key in input_dict:
    if input_dict[key][2] != -1:
        if input_dict[key][2] == 265834:
            continue
        y = list(output_dict[input_dict[key][2]])
        y[3] += 1
        output_dict[input_dict[key][2]] = y #1 se non e utxo, 0 altrimenti
        
tot_utxo = 0
top_utxo = (0,0) #trans,value
for key in output_dict:
    if output_dict[key][3] == 0: 
        y = list(tx_dict[output_dict[key][0]])
        if output_dict[key][2] > 0 :
            y[1] += output_dict[key][2]
        elif output_dict[key][2] < 0 :
            print(output_dict[key][2],'chiave output: ' + str(key))
            y[1] += 0
        tx_dict[output_dict[key][0]] = y

for key in tx_dict:
    if tx_dict[key][1] > top_utxo[1]:
        top_utxo = (key,tx_dict[key][1]) #id tx, valore utxo
    if tx_dict[key][1] > 0:
        tot_utxo += tx_dict[key][1]

out_id = 0
out_pk_id = 0
for key in output_dict:
    if top_utxo[0] == output_dict[key][0]:
        out_id = key
        out_pk_id = output_dict[key][1]
        
print('Tx : ' + str(top_utxo[0]),'Blocco: ' + str(tx_dict[top_utxo[0]][0]),'Output id : ' + str(out_id),
      'Address: ' + str(out_pk_id),'Valore: ' + str(top_utxo[1]* 10**(-8)))
print('Tot UTXO: ' + str(tot_utxo) + ' satoshi')
tot_utxo = tot_utxo * 10**(-8)         
print('Tot UTXO: ' + str(tot_utxo) + ' BTC')


# In[ ]:


#the distribution of the block occupancy, i.e. of the number of transactions in each block in the entire period of time.
block_occupancy = {} #key = n blocco, dim
for key in tx_dict:
    block = tx_dict[key][0]
    if block in block_occupancy:
         block_occupancy[block] += 1
    else:
        block_occupancy[block] = 1

h=[] #index blocco
k=[] #dim blocco

for key in block_occupancy:
        h.append(key)
        k.append(block_occupancy[key])
    
block_occupancy_dim = {} #key = dim
for key in block_occupancy:
    chiave = block_occupancy[key]
    if chiave in block_occupancy_dim:
         block_occupancy_dim[chiave] += 1
    else:
        block_occupancy_dim[chiave] = 1

x=[] #dim
y=[] #num
for key in block_occupancy_dim:
        x.append(key)
        y.append(block_occupancy_dim[key])
        
#support dicts    
occ1 = {}
for key in block_occupancy_dim:
    if block_occupancy_dim[key] not in occ1:
        occ1[block_occupancy_dim[key]] = key
        
occ2 = {}
for key in occ1:
    occ2[occ1[key]] = key

df = pd.DataFrame.from_dict(occ2,orient='index')
df.plot(title=" Distribution of the block occupancy",  ylabel="Number of Blocks",xlabel="Transactions",kind="line")


# In[ ]:


#show the evolution in time of the block size, by considering a time step of one month.
#considerando un tempo di 30g, e considerando che in media un blocco viene aggiunto alla bc ogni 10 minuti
#in media, il numero di blocchi minati in un mese di tempo è 4320
block_occupancy_month_tot = {}
i=0
for key in block_occupancy:
    if i == 0:
        block_occupancy_month_tot[key] = block_occupancy[key]
    i+=1
    if i == 4320:
        i=0
        block_occupancy_month_tot[key] = block_occupancy[key]

x=[] #dim
y=[] #num
i=0
for key in block_occupancy_month_tot:
        x.append(i)
        i+=1
        y.append(block_occupancy_month_tot[key])

plt.bar(x,y)
plt.show()

df = pd.DataFrame.from_dict(block_occupancy_month_tot,orient='index')

df.plot(title="Distribution of fees",  
    ylabel="BTC", 
    kind = 'hist'
    )


# In[ ]:


#the total amount of bitcoin received from each public key that has
#received at least one COINBASE transaction, in the considered period, and show a distribution of the value
coinbase_tx = {}

for key in input_dict:
    if input_dict[key][2] == -1 and input_dict[key][1] == 0:
        coinbase_tx[input_dict[key][0]] = 0 #aggiungo il numero della tx
        
account_ = {}

for key in output_dict:
    if output_dict[key][0] in coinbase_tx:
        if output_dict[key][1] not in account_:
            account_[output_dict[key][1]] = 0 #se non c'è già l'account, lo aggiungo

tot_for_account = {}
for key in output_dict:
    if output_dict[key][1] in account_:
        if output_dict[key][1] not in tot_for_account:
            tot_for_account[output_dict[key][1]] = output_dict[key][2]
        else:
            tot_for_account[output_dict[key][1]] += output_dict[key][2]
  

for key in tot_for_account:
    tot_for_account[key] = tot_for_account[key]*10**(-8)
    

top = (0,0)
for key in tot_for_account:
    if tot_for_account[key] > top[1]:
        top = (key,tot_for_account[key])

tot = {}
for key in tot_for_account:
    if tot_for_account[key] not in tot:
        tot[tot_for_account[key]] = key
print(len(tot))


df = pd.DataFrame.from_dict(tot_for_account,orient='index',columns=['BTC'])
df.plot(title="Amount of bitcoin for pubKey",ylabel='BTC',kind='hist', logy=True)


# In[ ]:


#the distribution of the fees spent in each transaction in the considered period.
coinbase_tx = {}

for key in input_dict:
   # print(input_dict[key])
    if input_dict[key][2] == -1 and input_dict[key][1] == 0:
        coinbase_tx[input_dict[key][0]] = 0 #aggiungo il numero della tx
        
tx = {}
for key in tx_dict:
    if key not in coinbase_tx:
        tx[key] = (0,0,0) #input,output,fee
        
for key in output_dict:
    if output_dict[key][0] in tx:
        y = list(tx[output_dict[key][0]])
        y[1] +=  output_dict[key][2]
        tx[output_dict[key][0]] = y
        
for key in input_dict:
    if input_dict[key][0] in tx:
        y = list(tx[input_dict[key][0]])
        y[0] +=  output_dict[input_dict[key][2]][2]
        tx[input_dict[key][0]] = y

#compute the fees
for key in tx:
    k = list(tx[key])
    k[2] =  (k[0] - k[1])*10**(-8)
    tx[key] = k
    
#support dicts
tx2 = {}
for key in tx:
    tx2[key] = tx[key][2]

tx3 = {}
for key in tx2:
    if tx2[key] != 0:
        tx3[key] = tx2[key]

df = pd.DataFrame.from_dict(tx3,orient='index')

df.plot(title="Distribution of fees",  
    ylabel="BTC",  
    )


# In[ ]:


input_dict2 = {}
for index,inp in enumerate(input_array):
    if inp.is_valid:
        input_dict2[inp.id_input] = (inp.id_trans,inp.sig_id,inp.output_id)

output_dict2 = {}
for index,out in enumerate(output_array):
    if out.is_valid:
        output_dict2[out.id_output] = (out.id_trans,out.pk_id,out.value,0)

tx_dict2 = {}
for index,tx in enumerate(tx_array):
    if tx.is_valid:
        tx_dict2[tx.id_trans] = (tx.block_id,0,[],[]) #id,tot_input,input,output

for key in input_dict2:
    tx_dict2[input_dict2[key][0]][2].append(key)
    
for key in output_dict2:
    tx_dict2[output_dict2[key][0]][3].append(key)
    
    


# In[ ]:


for key in input_dict2:
    y = list(tx_dict2[input_dict2[key][0]])
    if input_dict2[key][2] == -1:
        continue
    y[1] += output_dict2[input_dict2[key][2]][2] 
    tx_dict2[input_dict2[key][0]] = y


# In[ ]:


G = nx.Graph()

for key in input_dict2:
    if input_dict2[key][2] == -1:
        valore = 5000000000
    else:
        valore = output_dict2[input_dict2[key][2]][2]
    y = tx_dict2[input_dict2[key][0]][3] #prendo array output
    for elem in y:
        if tx_dict2[output_dict2[elem][0]][1] == 0:
            formulina = output_dict2[elem][2]*(valore/5000000000)
        else:
            formulina = output_dict2[elem][2]*(valore/tx_dict2[output_dict2[elem][0]][1])
        G.add_edges_from([(str(input_dict2[key][1]), str(output_dict2[elem][1]), {"weight" : formulina})])


# In[ ]:


list_nodes = list(G.nodes)
a = random.choice(list_nodes)
b = random.choice(list_nodes)
#node choose for the test were 103919 and 155526
print(a,b)
flow_value, flow_dict = nx.maximum_flow(G,a,b,capacity='weight')

print(flow_value)


# In[ ]:


print(a,b)
flow_value = nx.maximum_flow_value(G,a,b,capacity='weight')


# In[ ]:


#One basic metric for a node is its degree: how many edges it has.
print('Degree of node 103919: ' + str(G.degree["103919"]))
print('Degree of node 155526: ' + str(G.degree["155526"]))

pageranks = nx.pagerank(G) # A dictionary
print('Degree of node 155526: ' + str(pageranks["155526"]))
print('Degree of node 103919: ' + str(pageranks["103919"]))

