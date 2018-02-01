import pandas as pd
import numpy as np
import sys
import codecs

N_YEARS_STR = '6'
END_YEAR = 2017

#DOE SC Contracts
contracts = pd.read_pickle('../cleaned_data/sc_contracts.pkl')
contracts = contracts.rename(columns = {
    'dollarsobligated':'Amount ($)',
})

doe_state_list = []
contracts = contracts.dropna(subset=['placeofperformancecongressionaldistrict'])
for dist in contracts['placeofperformancecongressionaldistrict']:
    doe_state_list.append(str(dist[:2]))
contracts['place_of_performance_state'] = doe_state_list

contracts_by_state = contracts.groupby(['place_of_performance_state'])
contracts_by_district = contracts.groupby('placeofperformancecongressionaldistrict')

#DOE HEP grants
grants = pd.read_pickle('../cleaned_data/hep_grants.pkl')
grants = grants.rename(columns = {
    'Amount':'Amount ($)',
})

state_list = []
for state in grants['State']:
    if len(state) >2:
        state_list.append(state[1:])
    else:
        state_list.append(state)
grants['State'] = state_list
    
grants_by_district = grants.groupby(['District'])
grants_by_state = grants.groupby(['State'])

#NSF MPS Grants
nsf_grants = pd.read_pickle('../cleaned_data/nsf_mps_grants.pkl')
nsf_grants = nsf_grants.rename(columns = {
    'fed_funding_amount':'Amount ($)',
    'recipient_name' : 'Institution',
    'fiscal_year' : 'Year',
    'principal_place_state_code' : 'State'
})
nsf_by_state = nsf_grants.groupby(['State'])
nsf_by_district = nsf_grants.groupby(['cong_dist'])

#legislators = pd.read_pickle('../data/old_data/old_cleaned_data/legislator_key_info')
#committee_members = pd.read_pickle('../data/old_data/old_cleaned_data/committee_memberships').groupby(4)

legislators = pd.read_pickle('../cleaned_data/legislator_key_info.pkl')
committee_members = pd.read_pickle('../cleaned_data/committee_memberships.pkl').groupby(4)


def get_nsf_grants_by_district(distcode):
    try: 
        nsf_by_district.get_group(distcode)
    except KeyError: 
        print 'This district received no NSF MPS grants from 2012-'+str(END_YEAR)
        return
    print 'In the past '+N_YEARS_STR+' years, this district has received:', '${:,.2f}'.format(nsf_by_district.get_group(distcode)['Amount ($)'].sum()), 'in NSF MPS grants.'
    print nsf_by_district.get_group(distcode).groupby(['Institution','Year'])[['Amount ($)']].sum()
    
def get_nsf_grants_by_state(distcode):
    try: 
        nsf_by_state.get_group(distcode)
    except KeyError: 
        print 'This state received no NSF MPS grants from 2012-'+str(END_YEAR)
        return
    n_contracts = nsf_by_state.get_group(distcode)['Amount ($)'].count()
    total_contract_value = nsf_by_state.get_group(distcode)['Amount ($)'].sum()
    print 'In the past '+N_YEARS_STR+' years, this state has received:'
    print n_contracts, 'NSF MPS grants, totalling', '${:,.2f}'.format(total_contract_value)
    print ' '
    n_institutes = len(nsf_by_state.get_group(distcode).groupby(['Institution'])[['Amount ($)']])
    if n_institutes < 4:
        print nsf_by_state.get_group(distcode).groupby(['Institution','Year'])[['Amount ($)']].sum()
    else:
        print nsf_by_state.get_group(distcode).groupby(['Institution'])[['Amount ($)']].sum().sort_values(['Amount ($)'],ascending=False).head(n=10)
        if n_institutes > 10: print 'and ', n_institutes-10, ' other institutions.'
            
def get_state_contracts(distcode):
    try: 
        contracts_by_state.get_group(distcode)
    except KeyError: 
        print 'This state received no SC contracts from 2012-'+str(END_YEAR+1)
        return
    n_contracts = contracts_by_state.get_group(distcode)['Amount ($)'].count()
    total_contract_value = contracts_by_state.get_group(distcode)['Amount ($)'].sum()
    print 'In the past '+N_YEARS_STR+' years, this state has received:'
    print n_contracts, 'Office of Science contracts, totalling', '${:,.2f}'.format(total_contract_value)
    print ' '
    n_firms = len(contracts_by_state.get_group(distcode).groupby(['vendorname'])[['Amount ($)']])
    if n_firms < 4:
        print contracts_by_state.get_group(distcode).groupby(['vendorname','fiscal_year'])[['Amount ($)']].sum()
    else:
        print contracts_by_state.get_group(distcode).groupby(['vendorname'])[['Amount ($)']].sum().sort_values(['Amount ($)'],ascending=False).head(n=10)
        if n_firms > 10: print 'and ', n_firms-10, ' other firms.'

def get_state_grants(distcode):
    try: 
        grants_by_state.get_group(distcode)
    except KeyError: 
        print 'This state received no SC HEP grants from 2012-'+str(END_YEAR)
        return
    n_contracts = grants_by_state.get_group(distcode)['Amount ($)'].count()
    total_contract_value = grants_by_state.get_group(distcode)['Amount ($)'].sum()
    print 'In the past '+N_YEARS_STR+' years, this state has received:'
    print n_contracts, 'HEP grants, totalling', '${:,.2f}'.format(total_contract_value)
    print ' '
    n_institutes = len(grants_by_state.get_group(distcode).groupby(['Institution'])[['Amount ($)']])
    if n_institutes < 4:
        print grants_by_state.get_group(distcode).groupby(['Institution','Year']).sum()
    else:
        print grants_by_state.get_group(distcode).groupby(['Institution'])[['Amount ($)']].sum().sort_values(['Amount ($)'],ascending=False).head(n=10)
        if n_institutes > 10: print 'and ', n_institutes-10, ' other institutions.'
    
def tell_me_about_state(distcode):
    these_sens = legislators[legislators[1] == distcode+'-'+distcode]
    print '# ' + distcode + ' -- Sen. ' + these_sens[0].values[0] + ' (' + these_sens[2].values[0] + ') and ' + ' Sen. ' + these_sens[0].values[1] + ' (' + these_sens[2].values[1] + ')'
    print '## Committees'
    get_committee_info(these_sens[0].values[0],these_sens[4].values[0])
    get_committee_info(these_sens[0].values[1],these_sens[4].values[1])
    print '## HEP Grants'
    print '```'
    get_state_grants(distcode)
    print '```'
    print '## SC Contracts'
    print '```'
    get_state_contracts(distcode)
    print '```'
    print '## NSF MPS Grants'
    print '```'
    get_nsf_grants_by_state(distcode)
    print '```'
    
    
def get_district_contracts(distcode):
    try: 
        contracts_by_district.get_group(distcode)
    except KeyError: 
        print 'This district received no SC contracts from 2012-'+str(END_YEAR+1)
        return
    print 'In the past '+N_YEARS_STR+' years, this district has received:', '${:,.2f}'.format(contracts_by_district.get_group(distcode)['Amount ($)'].sum()), 'in SC contracts.'
    print contracts_by_district.get_group(distcode).groupby(['vendorname','fiscal_year'])[['Amount ($)']].sum()

def get_district_grants(distcode):
    try: 
        grants_by_district.get_group(distcode)
    except KeyError: 
        print 'This district received no SC HEP grants from 2012-'+str(END_YEAR)
        return
    print 'In the past '+N_YEARS_STR+' years, this district has received:', '${:,.2f}'.format(grants_by_district.get_group(distcode)['Amount ($)'].sum()), 'in SC HEP grants.'
    print grants_by_district.get_group(distcode).groupby(['Institution','Year']).sum()
    
    
def get_committee_info(repname,rep_bioid):
    try:
        committee_members.get_group(rep_bioid)
    except KeyError:
        print repname, 'is not on any of our key committees \n'
        return
    comms_for_this_rep = committee_members.get_group(rep_bioid)
    for i, commname in enumerate(comms_for_this_rep[3].values):
        print repname, 'is the', '#'+str(comms_for_this_rep[1].values[i]), comms_for_this_rep[2].values[i], 'on the', comms_for_this_rep[3].values[i],'\n'
        
        
def tell_me_about_district(distcode):
    if '-' in distcode:
        hyph_distcode = distcode
        unhyph_distcode = distcode[0:2] + distcode[3:]
    else:
        hyph_distcode = distcode[0:2] + '-' + distcode[2:]
        unhyph_distcode = distcode
    this_rep = legislators[legislators[1] == hyph_distcode]
    first_str = '## ' + hyph_distcode + ' -- Rep. '+ this_rep[0].values + ' (' + this_rep[2].values + ')' + ' -- [Wikipedia](https://en.wikipedia.org/wiki/'+hyph_distcode+')'
    if len(first_str) == 1:
        print first_str[0]
        print '### Committees'
        get_committee_info(this_rep[0].values[0],this_rep[4].values[0])
    else:
        print '## ' + hyph_distcode + ' Unknown Rep.'
    print '### HEP Grants'
    print '```'
    get_district_grants(hyph_distcode)
    print '```'
    print '### SC Contracts'
    print '```'
    get_district_contracts(unhyph_distcode)
    print '```'
    print '### NSF MPS Grants'
    print '```'
    get_nsf_grants_by_district(unhyph_distcode)
    print '```'
    
all_cong_dists = ['AL-01', 'AL-02', 'AL-03', 'AL-04', 'AL-05', 'AL-06', 'AL-07', 'AK-00', 'AZ-01', 'AZ-02', 'AZ-03', 'AZ-04', 'AZ-05', 'AZ-06', 'AZ-07', 'AZ-08', 'AZ-09', 'AR-01', 'AR-02', 'AR-03', 'AR-04', 'CA-01', 'CA-02', 'CA-03', 'CA-04', 'CA-05', 'CA-06', 'CA-07', 'CA-08', 'CA-09', 'CA-10', 'CA-11', 'CA-12', 'CA-13', 'CA-14', 'CA-15', 'CA-16', 'CA-17', 'CA-18', 'CA-19', 'CA-20', 'CA-21', 'CA-22', 'CA-23', 'CA-24', 'CA-25', 'CA-26', 'CA-27', 'CA-28', 'CA-29', 'CA-30', 'CA-31', 'CA-32', 'CA-33', 'CA-34', 'CA-35', 'CA-36', 'CA-37', 'CA-38', 'CA-39', 'CA-40', 'CA-41', 'CA-42', 'CA-43', 'CA-44', 'CA-45', 'CA-46', 'CA-47', 'CA-48', 'CA-49', 'CA-50', 'CA-51', 'CA-52', 'CA-53', 'CO-01', 'CO-02', 'CO-03', 'CO-04', 'CO-05', 'CO-06', 'CO-07', 'CT-01', 'CT-02', 'CT-03', 'CT-04', 'CT-05', 'DE-00', 'FL-01', 'FL-02', 'FL-03', 'FL-04', 'FL-05', 'FL-06', 'FL-07', 'FL-08', 'FL-09', 'FL-10', 'FL-11', 'FL-12', 'FL-13', 'FL-14', 'FL-15', 'FL-16', 'FL-17', 'FL-18', 'FL-19', 'FL-20', 'FL-21', 'FL-22', 'FL-23', 'FL-24', 'FL-25', 'FL-26', 'FL-27', 'GA-01', 'GA-02', 'GA-03', 'GA-04', 'GA-05', 'GA-06', 'GA-07', 'GA-08', 'GA-09', 'GA-10', 'GA-11', 'GA-12', 'GA-13', 'GA-14', 'HI-01', 'HI-02', 'ID-01', 'ID-02', 'IL-01', 'IL-02', 'IL-03', 'IL-04', 'IL-05', 'IL-06', 'IL-07', 'IL-08', 'IL-09', 'IL-10', 'IL-11', 'IL-12', 'IL-13', 'IL-14', 'IL-15', 'IL-16', 'IL-17', 'IL-18', 'IN-01', 'IN-02', 'IN-03', 'IN-04', 'IN-05', 'IN-06', 'IN-07', 'IN-08', 'IN-09', 'IA-01', 'IA-02', 'IA-03', 'IA-04', 'KS-01', 'KS-02', 'KS-03', 'KS-04', 'KY-01', 'KY-02', 'KY-03', 'KY-04', 'KY-05', 'KY-06', 'LA-01', 'LA-02', 'LA-03', 'LA-04', 'LA-05', 'LA-06', 'ME-01', 'ME-02', 'MD-01', 'MD-02', 'MD-03', 'MD-04', 'MD-05', 'MD-06', 'MD-07', 'MD-08', 'MA-01', 'MA-02', 'MA-03', 'MA-04', 'MA-05', 'MA-06', 'MA-07', 'MA-08', 'MA-09', 'MI-01', 'MI-02', 'MI-03', 'MI-04', 'MI-05', 'MI-06', 'MI-07', 'MI-08', 'MI-09', 'MI-10', 'MI-11', 'MI-12', 'MI-13', 'MI-14', 'MN-01', 'MN-02', 'MN-03', 'MN-04', 'MN-05', 'MN-06', 'MN-07', 'MN-08', 'MS-01', 'MS-02', 'MS-03', 'MS-04', 'MO-01', 'MO-02', 'MO-03', 'MO-04', 'MO-05', 'MO-06', 'MO-07', 'MO-08', 'MT-00', 'NE-01', 'NE-02', 'NE-03', 'NV-01', 'NV-02', 'NV-03', 'NV-04', 'NH-01', 'NH-02', 'NJ-01', 'NJ-02', 'NJ-03', 'NJ-04', 'NJ-05', 'NJ-06', 'NJ-07', 'NJ-08', 'NJ-09', 'NJ-10', 'NJ-11', 'NJ-12', 'NM-01', 'NM-02', 'NM-03', 'NY-01', 'NY-02', 'NY-03', 'NY-04', 'NY-05', 'NY-06', 'NY-07', 'NY-08', 'NY-09', 'NY-10', 'NY-11', 'NY-12', 'NY-13', 'NY-14', 'NY-15', 'NY-16', 'NY-17', 'NY-18', 'NY-19', 'NY-20', 'NY-21', 'NY-22', 'NY-23', 'NY-24', 'NY-25', 'NY-26', 'NY-27', 'NC-01', 'NC-02', 'NC-03', 'NC-04', 'NC-05', 'NC-06', 'NC-07', 'NC-08', 'NC-09', 'NC-10', 'NC-11', 'NC-12', 'NC-13', 'ND-00', 'OH-01', 'OH-02', 'OH-03', 'OH-04', 'OH-05', 'OH-06', 'OH-07', 'OH-08', 'OH-09', 'OH-10', 'OH-11', 'OH-12', 'OH-13', 'OH-14', 'OH-15', 'OH-16', 'OK-01', 'OK-02', 'OK-03', 'OK-04', 'OK-05', 'OR-01', 'OR-02', 'OR-03', 'OR-04', 'OR-05', 'PA-01', 'PA-02', 'PA-03', 'PA-04', 'PA-05', 'PA-06', 'PA-07', 'PA-08', 'PA-09', 'PA-10', 'PA-11', 'PA-12', 'PA-13', 'PA-14', 'PA-15', 'PA-16', 'PA-17', 'PA-18', 'RI-01', 'RI-02', 'SC-01', 'SC-02', 'SC-03', 'SC-04', 'SC-05', 'SC-06', 'SC-07', 'SD-00', 'TN-01', 'TN-02', 'TN-03', 'TN-04', 'TN-05', 'TN-06', 'TN-07', 'TN-08', 'TN-09', 'TX-01', 'TX-02', 'TX-03', 'TX-04', 'TX-05', 'TX-06', 'TX-07', 'TX-08', 'TX-09', 'TX-10', 'TX-11', 'TX-12', 'TX-13', 'TX-14', 'TX-15', 'TX-16', 'TX-17', 'TX-18', 'TX-19', 'TX-20', 'TX-21', 'TX-22', 'TX-23', 'TX-24', 'TX-25', 'TX-26', 'TX-27', 'TX-28', 'TX-29', 'TX-30', 'TX-31', 'TX-32', 'TX-33', 'TX-34', 'TX-35', 'TX-36', 'UT-01', 'UT-02', 'UT-03', 'UT-04', 'VT-00', 'VA-01', 'VA-02', 'VA-03', 'VA-04', 'VA-05', 'VA-06', 'VA-07', 'VA-08', 'VA-09', 'VA-10', 'VA-11', 'WA-01', 'WA-02', 'WA-03', 'WA-04', 'WA-05', 'WA-06', 'WA-07', 'WA-08', 'WA-09', 'WA-10', 'WV-01', 'WV-02', 'WV-03', 'WI-01', 'WI-02', 'WI-03', 'WI-04', 'WI-05', 'WI-06', 'WI-07', 'WI-08', 'WY-00']

#generate TOCs
previous_state = None
this_toc = None
this_str = None
tocs = []
for current_dist in all_cong_dists:
    current_state = current_dist[0:2]
    this_str = '['+current_dist+'](#'+current_dist+')  '
    if previous_state != current_state:
        tocs.append(this_toc)
        this_toc = this_str
    else:
        this_toc += this_str
    previous_state = current_state
tocs.append(this_toc)
tocs=tocs[1:]

previous_state = None
f = None
states_done = 0
for current_dist in all_cong_dists:
    current_state = current_dist[0:2]
    if previous_state != current_state:
        f = codecs.open('../docs/_states/'+current_state+'.md','w','utf-8')
        sys.stdout = f
        print '---'
        print 'title : ' + current_state
        print 'layout : datapage'
        print 'permalink : /states/'+current_state+'/'
        print '---'
        print '<a name=\"top\"></a>'
        print '[Project Homepage]({{ site.baseurl}}/)'
        print 
        print ''
        print tocs[states_done]
        states_done += 1
        print ''
        tell_me_about_state(current_state)
        print '---'
        print '---'
    print '<a name=\"'+current_dist+'\"></a>'
    print '[Back to top](#top)'
    tell_me_about_district(current_dist)
    print '---'
    previous_state = current_state