create table if not exists blog_content(
    id int(11) auto_increment,
    title varchar(200) not null,
    content text not null,
    createTime timestamp,
    primary key(id)
);

create table if not exists blog_account(
    id int(11) auto_increment,
    username varchar(20) not null,
    password varchar(32) not null,
    createTime timestamp,
    primary key(id),
    unique(username),
    key(username,password)
);

insert into blog_account(username,password) values('root','root');
