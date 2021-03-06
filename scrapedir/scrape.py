#! /usr/bin/env python3

import os
import requests
from lxml import html
import urllib.request
from multiprocessing import Pool
from multiprocessing import cpu_count


def crawl(P,GeneID,ENSGid,feed_dir):
    tree = html.fromstring(P.content)
    pARRAY = list()
    try:
        assert tree.xpath('//*[contains(@class, "cellThumbs ")][1]')[0] is not None
        len_div = len(tree.xpath('//*[contains(@class, "cellThumbs ")]')[1].getchildren())
        for i in range(1,len_div-1):
            try:
                pARRAY.extend(tree.xpath('//*[contains(@class, "cellThumbs ")][1]/div[{}]/a/@href'.format(i)))
            except:
                print('error')
        for IMG in pARRAY:
            print('grabbing {}'.format(IMG))
            rawname = '_'.join([ENSGid,GeneID,IMG.split("/")[-1]])
            name = '/'.join([feed_dir,rawname])
            urllib.request.urlretrieve("https:{}".format(IMG), name)
    except AssertionError:
        print(GeneID, ENSGid)
    except IndexError:
        pass


def image_parse(ENSGid='ENSG00000136997',GeneID='MYC',feed_dir='.'):
    print('initialized {}'.format(GeneID))
    print(ENSGid,GeneID)
    P = requests.get("https://www.proteinatlas.org/{}-{}/cell".format(ENSGid,GeneID))
    if P.status_code == 200:
        crawl(P,GeneID,ENSGid,feed_dir)
    else:
        print("https://www.proteinatlas.org/{}-{}/cell".format(GeneID,ENSGid))
        P = requests.get("https://www.proteinatlas.org/{}-{}/cell".format(GeneID.rstrip('\n'),ENSGid))
        if P.status_code == 200:
            crawl(P,GeneID,ENSGid,feed_dir)
        else:
            print("https://www.proteinatlas.org/{}-{}/cell does not contain IF images".format(GeneID,ENSGid))


def scrape(in_file):
    feed_dir = ''
    try:
        if os.path.isfile(in_file):
            feed_dir = '/'.join(in_file.split('/')[:-1])
            print('passes')
    except FileNotFoundError:
        print('input must be a directory')
        exit()

    # def image_parse(ENSGid='ENSG00000136997', GeneID='MYC'):
    #     print('initialized {}'.format(GeneID))
    #     print(ENSGid, GeneID)
    #     P = requests.get("https://www.proteinatlas.org/{}-{}/cell".format(ENSGid, GeneID))
    #     if P.status_code == 200:
    #         crawl(P, GeneID, ENSGid,feed_dir)
    #     else:
    #         print("https://www.proteinatlas.org/{}-{}/cell".format(GeneID, ENSGid))
    #         P = requests.get("https://www.proteinatlas.org/{}-{}/cell".format(GeneID.rstrip('\n'), ENSGid))
    #         if P.status_code == 200:
    #             crawl(P, GeneID, ENSGid,feed_dir)
    #         else:
    #             print("https://www.proteinatlas.org/{}-{}/cell does not contain IF images".format(GeneID, ENSGid))

    N = cpu_count()-1
    print("{} cores avail".format(N))
    with Pool(N) as p:
        try:
            with open(in_file) as f:
                loader = list()
                for line in f:
                    A,B = line.split('\t')[0].rstrip(' ').rstrip('\n'),line.split('\t')[1].lstrip(' ').rstrip('\n')
                    # print(repr(A),repr(B))
                    loader.append((A,B,feed_dir))
                    if len(loader) == N:
                        p.starmap(image_parse,loader)
                        loader = []
                p.starmap(image_parse,loader)
        except IndexError:
            print("./scrapedir INPUT.txt\nIn: two column, tab delimited list of GeneID and ENSGid.\
            UNIProt also works. ID orders do not matter. Row must be two entries.")


"""
PATH broken here



Debug examples:

P = requests.getdir("https://www.proteinatlas.org/ENSG00000136997-MYC/cell")
tree = html.fromstring(P.content)
tree.xpath('/html/body[1]/table/tr/td[2]/div[3]/table[4]/tr[4]/th[1]/table[2]/tbody')[0].getchildren()
#use tree.xpath('htmlpath') to call the object array from web, use indices [0-9] to access the object.
#check object with: {.tag,.text,.content,.getchildren(),.getparent()}

"""


