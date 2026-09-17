import streamlit as st
from datetime import datetime
import json

st.set_page_config(page_title='Veridian IT Copilot', page_icon='🛡️', layout='wide')

POLICIES = {
'password': ('KB-01','Self-service password reset. After 5 failed attempts or lockout, contact IT for manual unlock. No approval required.'),
'vpn': ('KB-02','Full-time employees receive VPN automatically. Contractors need manager approval through the access request form. Credentials expire every 90 days and must be renewed.'),
'laptop': ('KB-03 + Asset Policy','Laptop replacement is eligible after 3 years or earlier for verified hardware failure. Standard hardware refresh is 4 years. Early replacement outside the cycle needs Finance sign-off in addition to IT approval.'),
'software': ('KB-04','Catalog software can be self-installed. Non-catalog software requires IT Security review and normally takes 3–5 business days.'),
'printer': ('KB-05','Check the print queue and restart the print spooler. If the issue continues, create a ticket with the asset tag.'),
'mailbox': ('KB-06','Default mailbox quota is 25GB. Archive old mail. An increase above 25GB needs manager approval and is capped at 50GB.'),
'wifi': ('KB-07','Guest Wi-Fi credentials are available for 24 hours from the front-desk kiosk. Any employee can use it. No IT ticket is needed.'),
'expense': ('KB-08','Finance grants expense software access. IT handles login or technical issues after the account exists.'),
'security': ('KB-09','Report phishing, malware or unauthorized access immediately to security@veridian-corp.example. Do not forward it to other employees.'),
'wfh': ('KB-10','Employees working remotely more than 3 days/week may receive a one-time home-office equipment allowance. Manager sign-off and Finance processing are required. IT ships only after approval.')}

REQUESTS = [
('REQ-01','Aditi','Laptop dead, approximately 3.5 years old'),('REQ-02','Vikram','Needs guest Wi-Fi tomorrow'),('REQ-03','Karan','Locked out after password failed 6 times'),('REQ-04','Ritu','Needs a non-catalog data analysis tool'),('REQ-05','Sanjay','VPN credentials expired'),('REQ-06','Meera','Third-floor printer issue'),('REQ-07','Farhan','Works from home 4 days/week and wants a monitor'),('REQ-08','Ananya','Suspected phishing incident'),('REQ-09','Rohit','Mailbox full and cannot send emails'),('REQ-10','Kavya','Urgent admin access to finance reporting server'),('REQ-11','Nikhil','Contractor needs VPN next week'),('REQ-12','Sneha','Expense tool login invalid'),('REQ-13','Aman','Laptop screen flickers, 2 years old'),('REQ-14','Tanya','Approval to install productivity tracking extension'),('REQ-15','Rahul','Hey, can you help, it is not working?')]


def classify(text):
    t = text.lower()
    if any(x in t for x in ['phishing','malware','unauthorized access','suspicious email']): return 'security'
    if any(x in t for x in ['vpn','virtual private']): return 'vpn'
    if any(x in t for x in ['password','locked out','failed password']): return 'password'
    if any(x in t for x in ['laptop','screen flicker','computer','device']): return 'laptop'
    if 'expense' in t: return 'expense'
    if any(x in t for x in ['software','extension','install','tool']): return 'software'
    if any(x in t for x in ['printer','paper jam','print']): return 'printer'
    if any(x in t for x in ['mailbox','email full','cannot send']): return 'mailbox'
    if any(x in t for x in ['guest wi-fi','guest wifi','wi-fi','wifi']): return 'wifi'
    if any(x in t for x in ['monitor','home office','wfh','work from home']): return 'wfh'
    if any(x in t for x in ['admin access','server access','privileged']): return 'access'
    return 'unclear'


def analyze(text):
    cat = classify(text)
    base = {'category':cat.title(),'priority':'Normal','status':'Needs clarification','risk':'Unknown','confidence':'Low','route':'Employee → IT Helpdesk','source':'No policy selected','answer':'I need a little more information before routing this safely.','next':'Share the device/application name, exact error, when it started, and business impact.','missing':['Device or application','Exact error','When it started'],'decision':'The request is too vague to safely route.','approval':'Not determined'}
    if cat == 'unclear': return base
    source, policy = POLICIES.get(cat, ('Policy check','Use the supplied request details and do not grant access without documented authorization.'))
    base.update({'source':source,'answer':policy,'confidence':'High','missing':[],'decision':f'Request matched {source}. The route is based only on the supplied Veridian policy data.'})
    if cat == 'security':
        base.update(priority='Critical',status='Escalate to Security',risk='Critical',route='Employee → Security Team',next='Report immediately to security@veridian-corp.example. Do not forward the message to other employees.',approval='Security escalation required.')
    elif cat == 'password':
        base.update(priority='High',status='IT manual unlock',risk='High',route='Employee → IT Helpdesk → Manual unlock',next='IT must manually unlock the account after the reported 6 failed attempts.',approval='No approval required.')
    elif cat == 'vpn':
        base.update(status='Employee type check',risk='Medium',route='Employee → IT → Manager if contractor',next='Confirm employee type. Renew expired credentials. Contractors need manager approval via the access request form.',approval='Manager approval only for contractors.')
    elif cat == 'laptop':
        base.update(priority='High',status='Hardware assessment',risk='High',route='Employee → IT Hardware → Finance if early replacement',next='Verify hardware failure, check age against the 4-year refresh cycle, and route early replacement for required approvals.',approval='Finance sign-off plus IT approval may be required.')
    elif cat == 'software':
        base.update(status='Security review',risk='Medium',route='Employee → IT → IT Security',next='Check whether the item is in the approved catalog. Non-catalog software requires IT Security review and normally takes 3–5 business days.',approval='IT Security review required for non-catalog items.')
    elif cat == 'printer':
        base.update(status='Troubleshoot / ticket if unresolved',risk='Low',route='Employee → Self-service → IT ticket',next='Check print queue and restart print spooler. If unresolved, create a ticket with the asset tag.',approval='No approval stated.')
    elif cat == 'mailbox':
        base.update(status='Self-service first',risk='Low',route='Employee → Archive mail → Manager if quota increase',next='Archive old mail. Requests above 25GB need manager approval and cannot exceed 50GB.',approval='Manager approval above 25GB.')
    elif cat == 'wifi':
        base.update(status='Self-service',risk='Low',route='Employee → Front-desk kiosk',next='Use the front-desk kiosk for 24-hour guest Wi-Fi credentials. No IT ticket is needed.',approval='No approval required.')
    elif cat == 'expense':
        base.update(status='Finance / IT routing',risk='Medium',route='Employee → Finance for access / IT for login issue',next='Confirm whether the account already exists. Finance grants access; IT handles technical login issues afterward.',approval='Finance controls access.')
    elif cat == 'wfh':
        base.update(status='Manager + Finance approval',risk='Medium',route='Employee → Manager → Finance → IT Shipping',next='Confirm remote-work frequency, collect manager sign-off, send to Finance, and ship only after approval.',approval='Manager sign-off and Finance processing.')
    elif cat == 'access':
        base.update(priority='Critical',status='Access review required',risk='Critical',route='Employee → Manager / System owner → Security or IT',next='Do not grant privileged access from an urgent message alone. Collect business justification, requester identity, system scope and required duration.',approval='Explicit authorization and business justification required.')
    return base


def ticket_text(result, employee='Unknown', request_id='NEW'):
    return json.dumps({'ticket_id':request_id,'employee':employee,'created_at':datetime.now().isoformat(timespec='seconds'),'category':result['category'],'priority':result['priority'],'status':result['status'],'risk':result['risk'],'route':result['route'],'policy_evidence':result['source'],'recommended_action':result['next'],'approval':result['approval'],'missing_information':result['missing'],'decision_log':result['decision']}, indent=2)

st.title('🛡️ Veridian IT Copilot')
st.caption('Policy-grounded internal IT support agent • AIONOS Assignment 2 • Demo prototype')

with st.sidebar:
    st.header('Control Center')
    mode = st.radio('Choose workspace', ['Ask the Agent','Operations Overview','Evaluation Lab','Policy Explorer'])
    st.divider()
    st.info('Safety rule: use only the supplied Veridian data. Do not invent policies or claim that real tickets/emails were sent.')
    st.caption('Design focus: evidence, risk, routing, clarification and auditability')

if mode == 'Ask the Agent':
    st.subheader('Ask the Agent')
    examples = ['Custom question','My account is locked after 6 failed password attempts','I suspect a phishing email','I work from home 4 days per week and need a monitor','I need a non-catalog software installation','I need urgent admin access to a finance server','Hey, it is not working']
    selected = st.selectbox('Try an example', examples)
    question = st.text_area('Employee request', '' if selected == 'Custom question' else selected, height=110)
    employee = st.text_input('Employee name (optional)', 'Demo Employee')
    if st.button('Analyze Request', type='primary'):
        if not question.strip(): st.warning('Please enter a request.')
        else: st.session_state.result = analyze(question); st.session_state.question = question; st.session_state.employee = employee
    if 'result' in st.session_state:
        r = st.session_state.result
        st.divider(); st.subheader('Agent Decision Center')
        cols = st.columns(5)
        for c, label, value in zip(cols,['Category','Priority','Status','Risk','Confidence'],[r['category'],r['priority'],r['status'],r['risk'],r['confidence']]): c.metric(label,value)
        st.success(r['answer'])
        left,right = st.columns(2)
        with left:
            st.markdown('#### Recommended next action'); st.write(r['next'])
            st.markdown('#### Approval / routing path'); st.info(r['route'])
            st.markdown('#### Approval rule'); st.write(r['approval'])
        with right:
            st.markdown('#### Policy evidence'); st.code(r['source']); st.write(r['answer'])
            st.markdown('#### Missing-information check')
            st.write('No missing information detected for this demo.' if not r['missing'] else '\n'.join('• '+x for x in r['missing']))
            st.markdown('#### Why this decision?'); st.info(r['decision'])
        st.markdown('#### Ticket preview (not submitted)')
        raw = ticket_text(r, st.session_state.get('employee','Unknown'))
        st.code(raw, language='json')
        st.download_button('Download ticket JSON', raw, 'veridian_ticket.json', 'application/json')

elif mode == 'Operations Overview':
    st.subheader('Operations Command Center')
    results = [(rid,name,text,analyze(text)) for rid,name,text in REQUESTS]
    critical = sum(x[3]['priority']=='Critical' for x in results)
    high = sum(x[3]['priority']=='High' for x in results)
    normal = sum(x[3]['priority']=='Normal' for x in results)
    low = sum(x[3]['priority']=='Low' for x in results)
    clarify = sum(x[3]['status']=='Needs clarification' for x in results)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric('Requests',len(results))
    c2.metric('Critical',critical)
    c3.metric('High',high)
    c4.metric('Normal',normal)
    c5.metric('Low',low)
    c6.metric('Needs clarification',clarify)
    filter_value = st.selectbox('Filter by priority', ['All','Critical','High','Normal','Low'])
    for rid,name,text,r in results:
        if filter_value != 'All' and r['priority'] != filter_value: continue
        with st.expander(f'{rid} • {name} • {r["category"]} • {r["priority"]}'):
            st.write(text); st.write('**Status:**',r['status']); st.write('**Route:**',r['route']); st.write('**Action:**',r['next']); st.caption('Evidence: '+r['source'])

elif mode == 'Evaluation Lab':
    st.subheader('Evaluation Lab')
    st.write('This evaluates the lightweight routing logic against the 15 supplied employee requests. It is not a claim of production accuracy.')
    rows=[]
    for rid,name,text in REQUESTS:
        r=analyze(text); rows.append({'Request ID':rid,'Employee':name,'Detected category':r['category'],'Priority':r['priority'],'Status':r['status'],'Risk':r['risk'],'Evidence':r['source']})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.download_button('Export evaluation results', json.dumps(rows,indent=2), 'evaluation_results.json', 'application/json')

else:
    st.subheader('Policy Explorer')
    search = st.text_input('Search policy text or policy ID')
    for key,(source,text) in POLICIES.items():
        if not search or search.lower() in (key+' '+source+' '+text).lower():
            with st.expander(f'{source} • {key.title()}'):
                st.write(text)
