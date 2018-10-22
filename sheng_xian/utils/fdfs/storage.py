from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
class FDFSstorage(Storage):
    '''fdfs文件存储类'''

    def _open(self,name,mode="rb"):
        """打开文件是时候用"""
        pass
    def _save(self,name,content):
        """关闭文件候时候用"""
        #name：你选择上传的文件
        #content：包含你上传文件内容的File对象

        #创建一个client对象
        client=Fdfs_client('./utils/fdfs/client.conf')

        #上传文件到fast_dfs系统中
        res=client.upload_by_buffer(content.read())
        #上传成功会返回一个字典来提示信息
        #主要用两个参数来判断是否上传成功
        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': local_file_name,
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get("Status") !='Upload successed.':
            raise Exception('上传失败到fdfs')
        filename=res.get("Remote file_id")
        return filename
    def exists(self, name):
        """判断文件名是否可用"""
        return  False
    def url(self, name):
        """返回url文件名"""
        return name


