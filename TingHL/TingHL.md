## mongodb

```shell
mongo localhost:27018/admin  -u fact_admin -p 6fJEb5LkV2hRtWq0
mongo localhost:27018/admin -u fact_readonly RFaoFSr8b6BMSbzt
```
![](./Screenshot%20from%202020-05-02%2015-45-42.png)


MongInterface --> MongoInterfaceCommon --> BackEndDbInterface 

MongInterface 加载配置,认证,建立与数据库mongodb的链接
MongoInterfaceCommon 数据库mongodb封装的对外的接口
BackEndDbInterface 后台backend操作定义的一系列操作mongodb的函数

