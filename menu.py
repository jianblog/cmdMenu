#coding=utf-8

import json, yaml
import os, sys
import subprocess



class MenuNode(object):
    def __init__(self, title):
        self.children = []

        self.title = title
        self.__config = {}
        self.__cmd = []

    @property    # 参数属性
    def config(self):
        return self.__config
    @config.setter
    def config(self, conf):
        if type(conf) == type({}):
            self.__config = conf
        else:
            print("not a dict type: ", param)
            sys.exit(-1)

    @property    # 命令属性
    def cmd(self):
        return self.__cmd
    @cmd.setter
    def cmd(self, cmd):
        if type(cmd) == type([]):
            self.__cmd = cmd
        else:
            print("not a list type: ", cmd)
            sys.exit(-1)

    # 从父级节点继承config
    def extendconfig(self, conf):
        self.__config.update(conf)

    def addchild(self, child):
        self.children.append(child)


def parseMenu(item, upper=None):
    node = None
    if type(item) == type({}):
        node = MenuNode(item['title'])

        if 'cmd' in item:
            node.cmd = item['cmd']

        if 'config' in item:
            node.config = item['config']

        # 继承父节点的config
        if upper:
            node.extendconfig(upper.config)

        # 子节点添加到父节点children属性
        if 'child' in item:
            for n in item['child']:
                nd = parseMenu(n, node)
                node.addchild(nd)
    return node


def displayMenu(menulist, key=None):
    """
    菜单展示
    """
    os.system('clear')
    print("    *** 系统管理控制台 ***\n")
    menu_map = {}

    i = 1
    for l in menulist:
        appendix = '..'
        if l.cmd:
            appendix = ''
        menutext = str(i) + '. ' + l.title + appendix
        menu_map[str(i)] = l
        i += 1
        print("\t" + menutext + "\n")

        if l == key:
            j = 97    # 字母 a
            for subchild in l.children:
                appendix = '..'
                if subchild.cmd:
                    appendix = ''
                submenutext = chr(j) + '. ' + subchild.title + appendix
                menu_map[chr(j)] = subchild
                j += 1
                print("\t" + '   ' + submenutext +"\n")
    return menu_map


if __name__ == '__main__':
    dirname = os.path.split(os.path.realpath(__file__))[0]
    abspath = os.path.abspath(dirname)
    with open(os.path.join(abspath,'menu.yml'), 'r') as f:
        j = yaml.load(f)
        menu_struct = parseMenu(j)

    menu_saved = []     ##历史菜单入栈，用于返回
    menu_map = {}       ##当前菜单与按键映射

    menu_pos = menu_struct.children
    menu_hot = None

    while True:
        jenkins_cmd = "java -jar jenkins-cli.jar -s http://192.168.100.8:8078 -auth deploy:dfhx798 build "

        menu_map = displayMenu(menu_pos, menu_hot)
        inp = input("\n  请输入选择(r返回上级,x退出):")
        inp = inp.strip()
        if inp.lower() == 'r':
            if menu_hot:
                menu_hot = None
                menu_map = displayMenu(menu_pos, menu_hot)
            else:
                if len(menu_saved) > 0:
                    menu_pos = menu_saved.pop(-1)

        if inp.lower() == 'x':
            sys.exit()

        if inp.lower() in menu_map:
            if menu_map[inp].cmd:
                k = input("确认执行请按y,其他返回: ")
                if k != 'y':
                    continue
                print(menu_map[inp].cmd)

                jenkins_cmd += menu_map[inp].config['PROJ_NAME']
                for k, v in menu_map[inp].config.items():
                    if k == 'PROJ_NAME':
                        continue
                    config_str = ' -p ' + k + '=' + v
                    jenkins_cmd += config_str

                for c in menu_map[inp].cmd:
                    cmd_str = ' -p ' + c + '=true '
                    jenkins_cmd += cmd_str
                jenkins_cmd += ' -s -v '
                print(jenkins_cmd)

                ret = subprocess.Popen(jenkins_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=dirname)
                print("\n======>\n")

                if ret.stdout:
                    for line in ret.stdout:
                        line = line.decode('utf-8').strip()
                        print(line)
                    wait = input("\n任意键返回..")
            else:
                if inp.isdigit():
                    menu_hot = menu_map[inp]

                if inp.isalpha():
                    menu_saved.append(menu_pos) # 保存历史
                    menu_pos = menu_hot.children
                    menu_hot = menu_map[inp]
