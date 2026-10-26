/** The public Guard test edition has been retired. Product development is private. */
const RELEASE='guard-public-retired-20261017-r1';
const HEADERS={
 'X-Guard-Release':RELEASE,'Cache-Control':'no-store',
 'Content-Security-Policy':"default-src 'none'; script-src 'none'; style-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'",
 'X-Content-Type-Options':'nosniff','X-Frame-Options':'DENY',
 'Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin',
 'X-Robots-Tag':'noindex, nofollow, noarchive',
};
function response(request:Request,value:string,status:number,type='application/json; charset=utf-8'){
 return new Response(request.method==='HEAD'?null:value,{status,headers:{...HEADERS,'Content-Type':type}});
}
export async function handleGuardRequest(request:Request):Promise<Response|null>{
 const url=new URL(request.url);
 if(url.pathname!=='/guard'&&!url.pathname.startsWith('/guard/'))return null;
 const path=url.pathname.slice('/guard'.length)||'/';
 const readOnly=request.method==='GET'||request.method==='HEAD';
 if(path==='/api'||path.startsWith('/api/')){
  if(readOnly&&['/api/catalog','/api/public-intelligence'].includes(path)&&![...url.searchParams.keys()].some(key=>key!=='q')){
   return response(request,JSON.stringify({error:'guard_public_retired',private_enabled:false}),410);
  }
  return response(request,JSON.stringify({error:'site_test_private_disabled',private_enabled:false,deployment_mode:'retired'}),503);
 }
 if(path==='/'&&readOnly)return response(request,'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Guard — prueba pública retirada</title><main><h1>Guard: prueba pública retirada</h1><p>El desarrollo de Guard continúa en un entorno privado de acceso restringido.</p><p lang="en">The public Guard test edition has been retired. Development continues in a restricted private environment.</p><p><a href="/">CyberDailyLog · Volver al panel / Return to dashboard</a></p></main></html>',410,'text/html; charset=utf-8');
 return response(request,JSON.stringify({error:'guard_public_retired',private_enabled:false}),410);
}
