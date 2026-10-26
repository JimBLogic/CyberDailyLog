import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile,readdir} from 'node:fs/promises';
import {resolve,sep} from 'node:path';
import {Miniflare} from 'miniflare';
const root=resolve(import.meta.dirname,'../dist/server');
const modules=Object.fromEntries(await Promise.all((await readdir(root,{recursive:true})).filter(n=>n.endsWith('.js')).map(async n=>[n.split(sep).join('/'),{type:'esm',contents:await readFile(resolve(root,n),'utf8')}])));
test('compiled public Worker retires Guard without any provider request', {timeout:60000},async()=>{
 let calls=0;
 const mf=new Miniflare({host:'127.0.0.1',port:0,cf:false,telemetry:{enabled:false},workers:[{config:{name:'guard-retirement',compatibilityDate:'2026-10-16',compatibilityFlags:['nodejs_compat'],manifest:{mainModule:'index.js',modulesRoot:root,modules}},dev:{outboundService:{type:'fetcher',handler:async()=>{calls++;throw new Error('Retired Guard cannot contact providers')}}}}]});
 try{
  for(const path of ['/guard/','/guard/app.js','/guard/style.css','/guard/api/catalog','/guard/api/public-intelligence']){
   const r=await mf.dispatchFetch('https://retirement.invalid'+path,{headers:{Cookie:'fixture=private',Authorization:'Bearer forged'}});assert.equal(r.status,410);assert.equal(r.headers.get('location'),null);
  }
  const denied=await mf.dispatchFetch('https://retirement.invalid/guard/api/export?plan=pro');assert.equal(denied.status,503);assert.equal((await denied.json()).error,'site_test_private_disabled');assert.equal(calls,0);
 }finally{await mf.dispose()}
});
