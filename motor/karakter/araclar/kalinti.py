import cv2, numpy as np
def kalinti_maskesi(im):
    """Parşömen kalıntısı maskesi (alt gövde, açık krem bölgeler)."""
    al=im[...,3]>8; H=al.shape[0]
    L=cv2.cvtColor(im[...,:3],cv2.COLOR_BGR2LAB).astype(int)
    ch=np.hypot(L[...,1]-128,L[...,2]-128)
    alt=np.zeros_like(al); alt[int(H*0.55):]=True
    ten_degil=L[...,1]<=136
    A=al&alt&ten_degil&(L[...,0]>205)&(ch<22)
    seffaf_yakin=cv2.dilate((~al).astype(np.uint8),np.ones((7,7),np.uint8)).astype(bool)
    B=al&alt&ten_degil&(L[...,0]>186)&(ch<45)
    rm=np.zeros_like(al)
    for cand,kom in ((A,False),(B,True)):
        n,lab,st,_=cv2.connectedComponentsWithStats(cand.astype(np.uint8),8)
        for i in range(1,n):
            c=lab==i
            if st[i,4]>=(10 if kom else 4) and (not kom or (c&seffaf_yakin).any()): rm|=c
    ring=cv2.dilate(rm.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)&al&ten_degil&(L[...,0]>165)&(ch<48)
    return rm|ring
