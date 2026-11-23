(async () => {
 const configResponse = await fetch("/auth/config");
 if (!configResponse.ok) {
   document.querySelector("#message").textContent = "Authentication configuration is unavailable.";
   return;
 }
 const config = await configResponse.json();
 if (!config.supabase_url || !config.supabase_key) {
   document.querySelector("#message").textContent = "Supabase is not configured on the server.";
   return;
 }
 const sb = window.supabase.createClient(config.supabase_url, config.supabase_key);
 const form = document.querySelector("#auth-form");
 const msg = document.querySelector("#message");
 const submit = document.querySelector("#submit");
 form?.addEventListener("submit", async (e) => {
   e.preventDefault(); msg.textContent=""; submit.disabled=true; submit.textContent="Please wait…";
   const email=form.email.value.trim(), password=form.password.value;
   let result;
   if(form.dataset.mode==="signup") result=await sb.auth.signUp({email,password});
   else result=await sb.auth.signInWithPassword({email,password});
   if(result.error){msg.textContent=result.error.message;submit.disabled=false;submit.textContent=form.dataset.mode==="signup"?"Create account":"Sign in";return;}
   if(!result.data.session){msg.textContent="Check your email to confirm your account, then sign in.";submit.disabled=false;submit.textContent="Create account";return;}
   const session=result.data.session;
   const response=await fetch("/auth/session",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({access_token:session.access_token})});
   if(!response.ok){msg.textContent="Could not establish secure session. Please try again.";submit.disabled=false;return;}
   location.href="/dashboard";
 });
})();