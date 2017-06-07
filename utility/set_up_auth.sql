insert into django_site (id, domain, name) values(2, 'localhost:8000', 'Odin-local');
insert into socialaccount_socialapp (id,  provider, name, client_id, secret, key) values (1, 'github', 'OdinTestAuth', '569de618a31a05288965', '8b3e579286871247215a6b2a8e487244fad0db56', 'nope');
insert into socialaccount_socialapp_sites (id, socialapp_id, site_id) values (1, 1, 2);
