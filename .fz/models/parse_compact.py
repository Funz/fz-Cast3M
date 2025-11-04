#!/usr/bin/env python3
# Compact version of Cast3m output parser for embedding in JSON
import re,json,glob,csv,os
r={}
# MESS vars
if os.path.exists('castem.out'):
 for l in open('castem.out','r',errors='ignore'):
  if not l.strip().startswith('$'):
   m=re.search(r'([\w_]+)=([\d\.\+\-E]+)',l.split(';')[0],re.I)
   if m:
    try:r[m.group(1)]=float(m.group(2))
    except:r[m.group(1)]=float('nan')
# TXT files
for f in [f for f in glob.glob('*.txt') if f!='castem.out']:
 try:
  c=open(f,'r',errors='ignore').read().strip()
  try:r[os.path.splitext(f)[0]]=float(c)
  except:r[os.path.splitext(f)[0]]=c
 except:pass
# CSV files
for f in glob.glob('*.csv'):
 try:
  lines=list(csv.reader(open(f,'r',encoding='utf-8',errors='ignore'),delimiter=';'))
  if lines:
   cols=list(zip(*lines))
   try:
    float(cols[0][0])
    r[os.path.splitext(f)[0]]=[[float(v) for v in row] for row in lines if any(row)]
   except:
    for col in cols:
     try:r[col[0]]=[float(v) for v in col[1:] if v.strip()]
     except:pass
 except:pass
print(json.dumps(r))
