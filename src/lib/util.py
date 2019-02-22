import params
import time
import json
import os
import sys
import operator
import math
from math import *
import smtplib
from email.mime.text import MIMEText
import dateutil.parser

util_verbose = 0

def contains(L,x):
    for l in L:
        if (l==x): return True
    return False

def weighted_mean(M):
    if len(M)==0: return 0.0
    sum = 0.0
    weight = 0.0
    for wv in M:
        sum = sum + wv[0]*wv[1]
        weight = weight + wv[0]
    if weight != 0.0: return sum / weight
    else: return 0.0

def weighted_stddev(M):
    if len(M) <= 1: return 0.0
    sum = 0.0
    squared_sum = 0.0
    weight = 0.0
    for wv in M:
        sum = sum + wv[0]*wv[1]
        squared_sum = squared_sum + wv[0]*wv[1]*wv[1]
        weight = weight + wv[0]
    if weight != 0.0:
        sum = sum / weight
        squared_sum = squared_sum / weight
        if (squared_sum < sum*sum): return 0.0
        else: return math.sqrt(squared_sum - sum*sum)
    else: return 0.0

def min_of_column(M,n):
    if len(M)==0: return 0.0
    the_min = M[0][n]
    for i in range(1,len(M)):
        if M[i][n] < the_min: the_min = M[i][n]
    return the_min

def max_of_column(M,n):
    if len(M)==0: return 0.0
    the_max = M[0][n]
    for i in range(1,len(M)):
        if M[i][n] > the_max: the_max = M[i][n]
    return the_max
        
def extract_column(M,n):
    C = []
    for i in range(0,len(M)):
        C.append(float(M[i][n]))
    return C


#table de repartition de la normale centree reduite
NCR_max = 10.0
NCR_table = []
NCR_dx = 0.001

def fill_NCR_table():
    global NCR_table
    global NCR_dx
    global NCR_max
    sys.stdout.write("[computing NCR table ... ")
    k=1/sqrt(2*pi)
    x=0.0
    s=0.5
    while (x < NCR_max):
        f=k*exp(-0.5*x*x)
        s += f*NCR_dx
        NCR_table.append([x+NCR_dx,s])
        x += NCR_dx
    print("done]")

#fonction de repartition de la normale centree reduite
def proba_less_than_NCR(x):
    global NCR_table
    global NCR_max
    if (len(NCR_table)==0): fill_NCR_table()
    if x==0: return 0.5
    if x < 0: return 1.0 - proba_less_than_NCR(-x)
    if x > NCR_max: return 1.0
    a=0
    b=len(NCR_table)-1
    while ((b-a) > 1):
        i=int((a+b)/2)
        z=NCR_table[i][0]
        if (z<x): a=i
        else: b=i
    return NCR_table[a][1]

# proba that X less than x for X ~ normal(mu,sigma)
def proba_less_than_N(mu,sigma,x):
    return proba_less_than_NCR((x-mu)/sigma)

def send_email(msg, subject = ""): 
    mail = MIMEText('<font face="Courier New, Courier, monospace">'+html_format(msg)+'</font>')
    mail['Subject'] = 'jungle news : ' + subject
    mail['From'] = 'ly.olivier@gmail.com'
    mail['To'] = 'ly.olivier@gmail.com'
    mail.replace_header('Content-Type','text/html')
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("ly.olivier@gmail.com", param.smtp_pwd)
    server.send_message(mail)
    server.quit()

def get_public_ip_address():
    wget_proc = os.popen("wget http://checkip.dyndns.org/ -O - -o /dev/null | cut -d: -f 2 | cut -d\< -f 1", "r")
    pub_address = wget_proc.readlines()
    wget_proc.close()
    pub_address[0] = pub_address[0].replace(' ', '').replace('\n', '')
    return pub_address[0]

def now():
    return time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(time.time()))

def time_to_string(t):
    return time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(t))

def time_of_string(str):
    dt = dateutil.parser.parse(str)
    unix_t = time.mktime(dt.timetuple()) + 3600 * 1
    return unix_t

def tag_filename_with_time(unix_t, filename, suffix):
    return filename + time.strftime("-%Y-%m-%d--%H-%M-%S-UTC", time.gmtime(unix_t)) + suffix



## t in sec
def hour_min_sec(t):
    h=0
    m=0
    s=t
    while s > 3600:
        h += 1
        s -= 3600
    while s > 60:
        m += 1
        s -= 60
    if h>0:
        return "%02dh %02dmn" % (h,m)
    if m>0:
        return "%02dmn %02ds" % (m,s)
    else:
        return "%02ds" % (s)


def days_hour_min_sec(t):
    d=0
    h=0
    m=0
    s=t
    while s > 24*3600:
        d += 1
        s -= 24*3600
    while s > 3600:
        h += 1
        s -= 3600
    while s > 60:
        m += 1
        s -= 60
    if d>0:
        return "%2dd %02dh" % (d,h)
    if h>0:
        return "%2dh %02d" % (h,m)
    if m>0:
        return "%2dmn %02d" % (m,s)
    else:
        return "%02ds" % (s)

def write_in_string(pos, s1, s2):
    # write s2 after s1 at position pos and return the result
    if pos >= len(s1):
        for i in range(pos-len(s1)):
            s1 += ' '
        return s1 + s2
    else:
        return s1[:pos] + s2

def shorten_str(s, l):
    if s is None: return s
    if len(s) > l:
        if l < 3:
            return s[:l]
        else:
            return s[:l-2] + '..'
    else:
        return s

import math
import random


def cut_in_2_pieces(L):
    if len(L) == 0: return None
    if len(L) == 1: return L[0]
    if len(L) == 2: return (L[0]+L[1])/2
    list.sort(L)
    S = []
    S2 = []
    for l in L:
        if S == []:
            S.append(l)
            S2.append(l*l)
        else:
            S.append(l+S[-1])
            S2.append(l*l+S2[-1])
    M = S[-1]
    M2 = S2[-1]
    sigmas = {}
    for i in range(1,len(L)):
        s_g = float(S[i-1]) / i
        s2_g = float(S2[i-1]) / i
        s_d = float(M - S[i-1]) / (len(L)-i)
        s2_d = float(M2 - S2[i-1]) / (len(L)-i)
        d_g = s2_g - s_g*s_g
        d_d = s2_d - s_d*s_d
        if d_g < 0: d_g = 0
        if d_d < 0: d_d = 0
        sig_g = math.sqrt(d_g)
        sig_d = math.sqrt(d_d)
        sigmas[i] = (sig_g, sig_d, math.sqrt(sig_g*sig_g + sig_d*sig_d))
    m = None
    cut = None
    for k,v in sigmas.items():
        if m is None or m > v[2]:
            m = v[2]
            cut = k
    if cut == 0: return L[0]
    return (L[cut-1]+L[cut]) / 2

def bound(x,m,M):
    if x < m: return m
    if x > M: return M
    return x

def ubyte2short(b1,b2):
    sign = b2 > 127
    b = (b2 << 8) + b1
    c = (b ^ 0xffff)+1
    v = -c if sign else b 
    return v

def ubyte2uint(b1,b2,b3,b4):
    return b1 + (b2 << 8) + (b3 << 16) + (b4 << 24)
