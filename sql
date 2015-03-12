create table if not exists blog_content(
    id int(11) auto_increment,
    title varchar(200) not null,
    content text not null,
    createTime timestamp,
    primary key(id)
);
