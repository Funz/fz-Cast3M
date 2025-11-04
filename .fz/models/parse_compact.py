#!/usr/bin/env python3
# Compact version of Cast3m output parser
# This version uses minimal formatting to allow embedding in JSON if needed
import re,json,glob,csv,os
r={}
# MESS vars
if os.path.exists('castem.out'):
 with open('castem.out','r',errors='ignore') as f:
  for l in f:
   if not l.strip().startswith('$'):
    m=re.search(r'([\w_]+)=([\d\.\+\-E]+)',l.split(';')[0],re.I)
    if m:
     try:r[m.group(1)]=float(m.group(2))
     except ValueError:r[m.group(1)]=float('nan')
# TXT files
for fname in [f for f in glob.glob('*.txt') if f!='castem.out']:
 try:
  with open(fname,'r',errors='ignore') as f:
   c=f.read().strip()
  try:r[os.path.splitext(fname)[0]]=float(c)
  except ValueError:r[os.path.splitext(fname)[0]]=c
 except IOError:pass
# CSV files
for fname in glob.glob('*.csv'):
 try:
  with open(fname,'r',encoding='utf-8',errors='ignore') as f:
   lines=list(csv.reader(f,delimiter=';'))
  if lines:
   cols=list(zip(*lines))
   try:
    float(cols[0][0])
    r[os.path.splitext(fname)[0]]=[[float(v) for v in row] for row in lines if any(row)]
   except (ValueError, IndexError):
    for col in cols:
     try:r[col[0]]=[float(v) for v in col[1:] if v.strip()]
     except (ValueError, IndexError):pass
 except (IOError, csv.Error):pass
print(json.dumps(r))
