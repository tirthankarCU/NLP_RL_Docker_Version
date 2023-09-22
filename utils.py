import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns
import torch 
import torchvision.transforms as transforms
from PIL import Image
import cv2
import json 
from functools import cmp_to_key
suffix = [['easy','medium','hard','naive'],['fnlp_easy','fnlp_medium','fnlp_hard','fnlp_naive']]

def plot(data,ylb,title):
    plt.plot([i for i in range(1,)],data,color='mediumvioletred',marker='o')
    plt.title(title)
    plt.xlabel('Episodes')
    plt.ylabel(ylb)
    plt.savefig(f'results/{title}.png')

def crop_resize(img,dim=224):
    img=np.array(img)
    pil_image1=Image.fromarray(img)
    transform = transforms.Compose([
        transforms.Resize(dim),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )])
    return transform(pil_image1)

def crop_resize_cv2(img,dim=128):
    sz=(dim,dim)
    img_resized=cv2.resize(img,sz,interpolation = cv2.INTER_AREA)
    return img_resized

def phi(state):
    state_vis=state["visual"]
    state["visual"]=np.array(crop_resize(state_vis,dim=224))

def phiXtra(state):
    state_vis=state["visual"]
    state["visual"]=np.array(crop_resize_cv2(state_vis,dim=128))
    state["visual"]=np.mean(state["visual"],axis=2) # Reduce channel

def oneHot(mx,x):
    return torch.tensor([0 if i!=x else 1 for i in range(mx)]).unsqueeze(0)

unique_name={}
name_len=10
def save(state):
    new_name=""
    while True:
        new_name_arr=[ chr(ord('a')+np.random.randint(0,name_len)) for x in range(name_len) ]
        for ch in new_name_arr:
            new_name+=ch
        if new_name not in unique_name:
            unique_name[new_name]=True 
            break 
    with open(f"save_state/{new_name}.json",'w') as f:
        state["visual"]=state["visual"].tolist()
        json.dump(state,f)
    return new_name

def delete(state):
    del unique_name[state]

def get(state):
    f=open(f'save_state/{state}.json')
    data=json.load(f)
    state=data
    state["visual"]=np.array(state["visual"])
    return state

def pre_process(state):
    state["visual"] = torch.FloatTensor([state["visual"]])
    temp_vis=torch.squeeze(state["visual"])
    temp_vis=temp_vis.transpose(0,1).transpose(0,2) 
    state["visual"]=torch.unsqueeze(temp_vis,dim=0)
    return state["visual"]

def pre_process_text(model,state):
    TEXT = state["text"]+" [PAD]"*model.mxSentenceLength 
    text = model.tokenizer(TEXT,padding=True,truncation=True,max_length=model.mxSentenceLength,return_tensors="pt")
    return text 

def gen_data_random(opt, args):
    if opt<0: return [], []
    global suffix
    def sum_digits(no)->int:
        res=0
        while no!=0:
            m=no%10
            res+=m 
            no=no//10
        return res 
    valid=[]
    for i in range(1,1000):
        if opt==0 and sum_digits(i)<=9:
            valid.append(i)
        elif opt==1 and sum_digits(i)<=15:
            valid.append(i)
        elif opt==2:
            valid.append(i)
    def compare(i1,i2):
        return sum_digits(i1) - sum_digits(i2)
    m=int(len(valid)*0.1)
    np.random.shuffle(valid)
    train, test = valid[:m],valid[m:]
    train = sorted(train,key=cmp_to_key(compare))
    test = sorted(test,key=cmp_to_key(compare))
    with open(f'results/train_set{suffix[args["model"]][args["ease"]]}.json', 'w') as file:
        json.dump(train, file)
    with open(f'results/test_set{suffix[args["model"]][args["ease"]]}.json', 'w') as file:
        json.dump(test, file)
    return train, test

def gen_data_natural(args):
    total_set = [i for i in range(1, 1000)]
    # Controls how much data is there in test set.
    m=5
    train, test = None, None
    train = total_set[:m] + total_set[9:9+m] + total_set[99:99+m] + \
            total_set[199:199+m] + [total_set[299]] 
    test = total_set[m:2*m] + total_set[9+m:9+2*m] + total_set[99+m:99+2*m] + \
           total_set[199+m:199+2*m] + total_set[300:]
    with open(f'results/train_set{suffix[args["model"]][args["ease"]]}.json', 'w') as file:
        json.dump(train, file)
    with open(f'results/test_set{suffix[args["model"]][args["ease"]]}.json', 'w') as file:
        json.dump(test, file)
    return train, test
