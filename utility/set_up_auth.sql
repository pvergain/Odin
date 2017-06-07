insert into django_site (id, domain, name) values(2, 'localhost:8000', 'Odin-local');
insert into socialaccount_socialapp (id,  provider, name, client_id, secret, key) values (1, 'github', 'OdinTestAuth', 'example-client-id', 'example-secret-key', 'nope');
insert into socialaccount_socialapp_sites (id, socialapp_id, site_id) values (1, 1, 2);
