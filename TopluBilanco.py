import requests
from bs4 import BeautifulSoup
import pandas as pd

hisseler=[] #Hisselerin listesi. Bu listeye kazınan hisseler eklenir.
url="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse=ACSEL" #İş Yatırım web sitesindeki hisse detaylarını içeren URL. 
r=requests.get(url) #Belirtilen URL'e HTTP GET isteği gönderdik
s=BeautifulSoup(r.text,"html.parser") #HTTP yanıtının içeriğini BeautifulSoup kullanarak ayrıştırdık ve s değişkenine kaydettik. (kaynak sayfasındaki bilgileri cektik. )
s1=s.find("select",id="ddlAddCompare")
c1=s1.findChild("optgroup").findAll("option")

for a in c1:
    hisseler.append(a.string)
    

for i in hisseler:
    hisse=i
    tarihler=[]
    yıllar=[]
    donemler=[]

    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/sirket-karti.aspx?hisse="+hisse #Şu anki hissenin detaylarını içeren URL'yi oluşturduk.
    r1=requests.get(url1)
    soup=BeautifulSoup(r1.text,"html.parser")
    secim=soup.find("select",id="ddlMaliTabloFirst")
    secim2=soup.find("select",id="ddlMaliTabloGroup")

    try: #Herhangi bir hissede dönem bulamazsa hata vermeden devam etmesi icin try blogunu kullandık
        kids=secim.findChildren("option")
        if secim2 is not None:
            grup=secim2.find("option")["value"]
        else:
            grup = None

        for i in kids:
            tarihler.append(i.string.rsplit("/"))

        for j in tarihler: #Yıl ve dönemleri parcaladık
            yıllar.append(j[0])
            donemler.append(j[1])
        
        if len(tarihler) >=4:
            parametreler=(
                ("companyCode",hisse),
                ("exchange","TRY"),
                ("financialGroup",grup),
                ("year1",yıllar[0]),
                ("period1",donemler[0]),
                ("year2",yıllar[1]),
                ("period2",donemler[1]),
                ("year3",yıllar[2]),
                ("period3",donemler[2]),
                ("year4",yıllar[3]),
                ("period4",donemler[3]))
                
            url2="https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/MaliTablo"
            r2=requests.get(url2,params=parametreler).json()["value"]
            veri=pd.DataFrame.from_dict(r2)
            veri.drop(columns=["itemCode","itemDescEng"],inplace=True)
            print(veri)
        else:
            continue
    except AttributeError:
        continue

    del tarihler[0:4]
    tumveri=[veri]

    for _ in range(0,int(len(tarihler)+1)):
        if len(tarihler)==len(yıllar):
            del tarihler[0:4]
        else:
            yıllar=[]
            donemler=[]
            for i in tarihler:
                yıllar.append(i[0])
                donemler.append(i[1])
        
            if len(tarihler) >=4:
                parametreler2=(
                    ("companyCode",hisse),
                    ("exchange","TRY"),
                    ("financialGroup",grup),
                    ("year1",yıllar[0]),
                    ("period1",donemler[0]),
                    ("year2",yıllar[1]),
                    ("period2",donemler[1]),
                    ("year3",yıllar[2]),
                    ("period3",donemler[2]),
                    ("year4",yıllar[3]),
                    ("period4",donemler[3]))
                
                r3=requests.get(url2,params=parametreler2).json()["value"]
                veri2=pd.DataFrame.from_dict(r3)
                try:
                    veri2.drop(columns=["itemCode","itemDescEng","itemDescTr"],inplace=True)
                    tumveri.append(veri2)
                except KeyError:
                    continue
    
    veri3=pd.concat(tumveri,axis=1)
    baslık=["Bilanço"]

    for i in kids:
        baslık.append(i.string)

    baslıkfarkı=len(baslık)-len(veri3.columns)

    if baslıkfarkı!=0: #Eğer baslıkfarkı değeri sıfırdan farklı ise, baslık listesinin sonundan baslıkfarkı kadar eleman silinerek sütun başlıkları sayısının veri3 DataFrame nesnesinin sütun sayısına eşitlenmesi sağlanır.
        del baslık[-baslıkfarkı:]

    veri3.set_axis(baslık,axis=1,inplace=True)
    veri3[baslık[1:]]=veri3[baslık[1:]].astype(float)
    veri3.fillna(0,inplace=True)

    veri3.to_excel("Py dosyasının bulundugu dizin/{}.xlsx".format(hisse),index=False) #Hisse isimlerine göre ayrı excellerde veri ceksin
