from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
import binascii
import pyrx
import struct
import json
import os
import time
#import multiprocessing 
import sys
 
nicehash = False
app = FastAPI()

def insert_one(p_blob,p_height,p_job_id,p_target,p_seed_hash):
        os.environ["blob"] = p_blob
        os.environ["target"] = p_target
        os.environ["job_id"] = p_job_id
        os.environ["height"] = str(p_height)
        os.environ["seed_hash"] = p_seed_hash
def f_provjeri(p_blob,p_height,p_job_id,p_target,p_seed_hash):
    if ((os.environ["blob"] == p_blob) and (os.environ["target"] == p_target) and (os.environ["job_id"] == p_job_id) and (os.environ["height"] == str(p_height)) and (os.environ["seed_hash"] == p_seed_hash)):
        return {'nonce': os.environ["nonce"],'result': os.environ["hash"],'job_id': os.environ["job_id"],'status': os.environ["status"]}
    else:
        return {'nonce': '0','result': '0','job_id': '0', 'status': os.environ["status"]}

def f_provjeri_worker(p_blob,p_height,p_job_id,p_target,p_seed_hash):
    if ((os.environ["blob"] == p_blob) and (os.environ["target"] == p_target) and (os.environ["job_id"] == p_job_id) and (os.environ["height"] == str(p_height)) and (os.environ["seed_hash"] == p_seed_hash)):
        return True
    else:
        return False

def f_provjeri_hash():
    if ((os.environ["blob"] == p_blob) and (os.environ["target"] == p_target) and (os.environ["job_id"] == p_job_id) and (os.environ["height"] == str(p_height)) and (os.environ["seed_hash"] == p_seed_hash) and (os.environ["hash"] == '0')):
        return True
    else:
        return False

def pack_nonce(blob, nonce):
    b = binascii.unhexlify(blob)
    bin = struct.pack('39B', *bytearray(b[:39]))
    bin += struct.pack('I', nonce)
    bin += struct.pack('{}B'.format(len(b)-43), *bytearray(b[43:]))
    return bin

def worker(blob,target,job_id,height,seed_hash,n,start,step,duration):
    os.environ["status"] = 'working'
    p_start= start
    p_step= step
    p_duration= duration
    print('Start: ' + time.ctime(time.time()))
    started = time.time()
    hash_count = 0
    block_major = int(blob[:2], 16)
    printed=0
    cnv = 0
    if block_major >= 7:
        cnv = block_major - 6
    if cnv > 5:
        seed_hash = binascii.unhexlify(seed_hash)
    target = struct.unpack('I', binascii.unhexlify(target))[0]
    if target >> 32 == 0:
        target = int(0xFFFFFFFFFFFFFFFF / int(0xFFFFFFFF / target))
    nonce = p_start
    list1 = []
    while 1:
        bin = pack_nonce(blob, nonce)
        if cnv > 5:
            hash = pyrx.get_rx_hash(bin, seed_hash, height)
        hash_count += 1
        hex_hash = binascii.hexlify(hash).decode()
        r64 = struct.unpack('Q', hash[24:])[0]
        if r64 < target:
            elapsed = time.time() - started
            hr = int(hash_count / elapsed)
            p_nonce = binascii.hexlify(struct.pack('<I', nonce)).decode()
            p_result = hex_hash
            dict1= {'nonce': p_nonce, 'result': p_result, 'job_id': job_id}
            list1.append(dict1)
            print('Submitting hash: {}'.format(hex_hash))
            os.environ["hash"] = p_result
            os.environ["nonce"] = p_nonce
            os.environ["status"] = 'end'
            os.environ["hashrate"] = str(hr)
            ##upisi hash i nonce u bazu za tekuci blob
            break
        nonce += p_step
        elapsed = time.time() - started
        if elapsed > p_duration:
            hr = int(hash_count / elapsed)
            dict1= {'nonce': '0', 'result': '0','job_id': '0'}
            os.environ["hash"] = '0'
            os.environ["nonce"] = '0'
            os.environ["status"] = 'end'
            os.environ["hashrate"] = str(hr)
            list1.append(dict1)
            break
        ##za svako 100ti hash_count provjeriti da li je upisan nonce i hash za postojeci blob, ako jeste break
        if (hash_count % 100) == 0:
            if os.environ["blobstop"] == '1':
                hr = int(hash_count / elapsed)
                dict1= {'nonce': '0', 'result': '0','job_id': '0'}
                os.environ["hash"] = '0'
                os.environ["nonce"] = '0'
                os.environ["status"] = 'end'
                os.environ["hashrate"] = str(hr)
                #os.environ["blobstop"] = 0
                list1.append(dict1)
                break
        ####
    elapsed = time.time() - started
    hr = int(hash_count / elapsed)
    print('Hashrate: {} H/s'.format(hr))
    print('End: ' + time.ctime(time.time()))
    print(list1)#return list1


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/RandomXstart")
async def rx_start(request : Request):
    req_json = await request.json()
    p_blob = req_json['blob']
    p_target = req_json['target']
    p_job_id = req_json['job_id']
    p_height = req_json['height']
    p_seed_hash = req_json['seed_hash']
    insert_one(p_blob,p_height,p_job_id,p_target,p_seed_hash)
    return {"Poruka" : "Unseno"}

@app.post("/RandomXstop")
async def rx_start(request : Request):
    os.environ["blobstop"] = '1'
    while os.environ["status"] != 'end':
        time.sleep(1)
    os.environ["blobstop"] = '0'
    return {"Poruka" : "Unseno"}

@app.post("/RandomXprovjeri")
async def rx_provjeri(request : Request):
    req_json = await request.json()
    p_blob = req_json['blob']
    p_target = req_json['target']
    p_job_id = req_json['job_id']
    p_height = req_json['height']
    p_seed_hash = req_json['seed_hash']
    rez = f_provjeri(p_blob,p_height,p_job_id,p_target,p_seed_hash)
    return {'blob': os.environ["blob"],'nonce': os.environ["nonce"],'result': os.environ["hash"],'job_id': os.environ["job_id"],'status': os.environ["status"],'server': os.environ["server"],'hashrate':os.environ["hashrate"]}

@app.post("/RandomX")

async def proc_post(n : int, start : int, step : int, duration : int,request : Request,background_tasks: BackgroundTasks):
    req_json = await request.json()
    blob = req_json['blob']
    target = req_json['target']
    job_id = req_json['job_id']
    height = req_json['height']
    seed_hash = req_json['seed_hash']
    ##provjeriti da li ima u bazi i ako nema, upisati
    ##if f_provjeri_worker(blob,height,job_id,target,seed_hash) == False:
    insert_one(blob,height,job_id,target,seed_hash)
    os.environ["hash"] = '0'
    os.environ["nonce"] = '0'
    background_tasks.add_task(worker, blob, target,job_id,height,seed_hash,n,start,step,duration)
    return {"messagea": str(blob)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)