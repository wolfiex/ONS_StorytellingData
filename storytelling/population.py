'''
The processing file for all things population based. 

'''
from . import config
from . import lookups   
from .density import get_density
# import config
# import .config
# import .lookups
import pandas as pd




# consts 
lad = lookups.neighbours.index.to_list()



####### Functions ########

def get_population_data():
    ''' 
    Gets the population of the country from the MF tables for each year.
```
    Returns: ::list:: [::dict:: population, ::dict:: population_delta]
    ```
    '''
    population = {}
    for category in config.CATEGORIES:
        # male female table
        mf = pd.read_csv(''.join([config.CSVTABLES,getattr(config,category),config.simpletable['mf'],'.csv']),index_col=0)
        total_population = mf.sum(axis=1)

        population[category] = total_population.astype(int)

    population_diff = (population['SECONDARY'] - population['PRIMARY'])
    population_delta =  population_diff/population['PRIMARY']*100

    return [population,population_delta.to_dict(),population_diff.to_dict()]


def get_country_rank():
    ''' 
    Gets the rank of the country based on the total population of the country.

    For each Category: 
       
        1. Order the numbers

        For each Country:
            2. Filter by country
            3. Get country length
            4. Rank
            5. Recombine
```
        returns ::dict:: {'PRIMARY':{'rankings','length'},'SECONDARY':{'rankings','length'}}
    ```
    '''
    country_rank = {}
    for category in config.CATEGORIES:
        #  sort by descending by multiplying key by -1
        ordered = sorted(lad, key=lambda d: -population[category].loc[d])  
        total = {}
        result = []

        for country in ['England','Wales']:

            selection = list(filter(lambda x: x[0] == country[0], ordered))
            ranking = [[j,i+1] for i,j in enumerate(selection)]

            result.extend(ranking)
            # add the total count too for reference
            result.append(['all',len(selection)])

            total[country] = dict(result)
        country_rank[category] = total
    
    return country_rank




def rank_calculator(group):
    '''
    Number group items
```
    input ::dataframe:: group
    output ::dict:: key == code, value == rank
    ```
    '''
    dummy = group.sort_values(0)[0]
    return dict_zip(dict(zip(dummy.index,range(1,len(dummy)+1))))

def get_rankings(grain):
    ''' 
    Gets the rankings for the given category and grain.
```
    input: ::str:: grain
    output: rank
    ```
    '''
    rank = {}
    for cat in config.CATEGORIES:    
        rank[cat] = pop_group[cat].groupby(grain).apply(rank_calculator)
    return rank




def all_here(df,group,area,code):
    '''
    A function that lists the current ranking against the total number of items in the group.
    ```
    input: ::dataframe:: df
                ::str:: group (e.g. PRIMARY)
                ::str:: area (e.g. England)
                ::str:: code (e.g. LAD geocode)
    output: ::dict:: {'rank','all'}
    ```
    '''
    return dict(here = df[group][area][code], all = df[group][area]['all'])







def get_population(code,LA=True):
    '''
    Gets the local authority statistics for the given code.

    ```
    input: ::str:: code
           ::bool:: LA (default True) - is it a local authority or not?
    output: ::dict:: local authority
    ```
    '''


    ABS = {config.PRIMARY_NAME:population['PRIMARY'].loc[code], config.SECONDARY_NAME:population['SECONDARY'].loc[code]}

    ABS_CHANGE = {f'FROM{config.PRIMARY_NAME[1:]}TO{config.SECONDARY_NAME[1:]}':int(population_diff[code])}

    PC_CHANGE = {f'FROM{config.PRIMARY_NAME[1:]}TO{config.SECONDARY_NAME[1:]}':'%.2f'%population_delta[code]}

    if LA:

        if code[0] == 'E':country = 'England'
        else:country = 'Wales'

        COUNTRY_RANK = {config.PRIMARY_NAME:all_here(country_rank,'PRIMARY',country,code),
        config.SECONDARY_NAME:all_here(country_rank,'SECONDARY',country,code)
        }
    
        return dict(ABS=ABS,ABS_CHANGE=ABS_CHANGE,PC_CHANGE=PC_CHANGE,COUNTRY_RANK=COUNTRY_RANK,**get_density(code))

    else:
        return dict(ABS=ABS,ABS_CHANGE=ABS_CHANGE,PC_CHANGE=PC_CHANGE)


def group_classification(population):
    ''' 
    Insert group classification data into the population dataframe.

    ```
    input: ::df:: population
    output: ::df::
    '''

    pop_group = {}
    for cat in config.CATEGORIES:
                
        ponly = pd.DataFrame(population[cat].loc[lad]).astype(int)
        ponly['REGION'] = [lookups.lad2rgn[i] for i in ponly.index]
        ponly['COUNTRY'] = [i[0] for i in ponly.index]

        pop_group[cat] = ponly
    
    return pop_group



####### End Functions ########




population,population_delta,population_diff = get_population_data()
country_rank = get_country_rank()
pop_group = group_classification(population)














