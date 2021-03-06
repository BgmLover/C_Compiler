from backend.mips_writer import MIPSWriter
from backend.regs import Regs,Reg,Liveness_analysis
#寄存器 我感觉这个不够啊 没有zero 但是我现在不敢轻举妄动
normal_regs=['t1','t2','t3','t4','t5','t6','t7','t8','t9','s0','s1','s2','s3','s4','s5','s6','s7']

class Translator:
  mips_writer=None
  regs=None
  code_lines=None
  line_no=None

  def __init__(self,file_name,path):
    self.code_lines=self.Load_Inter(file_name)
    self.mips_writer=MIPSWriter(path)
    self.regs=Regs(self.code_lines,self.mips_writer)
    self.line_no=-1

  def Load_Inter(self,filename):
    lines=[]
    file=open(filename,'r',encoding='utf-8')
    for line in file:#中间代码
      line = line.replace('\r','').replace('\n','') #换行分割
      if line == '': #line没有内容 跳过
        continue
      lines.append(line.split(' ')) #放入list里
    return lines


  def function_call(self,function_name, params):
    saved_regs = ['ra'] + normal_regs
    # use_amount += 4
    # self.mips_writer.addi('sp', 'sp', -use_amount)
    # self.mips_writer.sw('ra', 'sp', 4)
    # self.mips_writer.addi('sp', 'sp', use_amount)
    use_amount = len(saved_regs)*4
    self.mips_writer.addi('sp', 'sp', -use_amount)
    count = 0
    for reg in saved_regs:
      self.mips_writer.sw(reg, 'sp', count)
      count += 4
    # self.mips_writer.addi('sp', 'sp', use_amount)
    param_count = 0
    for param in params:
      param_count += 1
      if param_count <= 4:
        self.mips_writer.addi(
          'a'+str(param_count-1),
          self.regs.get_normal_reg(param, self.line_no)
        )
      # else:
      #   use_amount += 4
      #   self.mips_writer.addi('sp', 'sp', -use_amount)
      #   self.mips_writer.sw(self.regs.get_normal_reg(param,self.line_no), 'sp')
      #   self.mips_writer.addi('sp', 'sp', use_amount)
    self.mips_writer.jal(function_name)
    # self.mips_writer.addi('sp', 'sp', -use_amount)
    count = 0
    for reg in saved_regs:
      self.mips_writer.lw(reg, 'sp', count)
      count += 4
    self.mips_writer.addi('sp', 'sp', use_amount)


  def function_return(self, variable=None):
    if variable is not None:
      if variable[0]=='t':
        self.mips_writer.addi('v0', self.regs.get_normal_reg(variable,self.line_no))
      else:
        self.mips_writer.addi('v0','zero',variable)
    self.mips_writer.jr('ra')


  #翻译成汇编
  def translate(self):
    self.line_no=0
    for line in self.code_lines:
      if line[0]=='LABEL': #LABEL n: -> n:
        self.mips_writer.write_label(line[1])
      if line[1]==':=': #left := right ->
        dst=self.regs.get_normal_reg(line[0],self.line_no)
        #数组形式 TODO
        src1=self.regs.get_normal_reg(line[2],self.line_no)
        src2=self.regs.get_normal_reg(line[-1],self.line_no)
        constant=line[-1]
        if len(line)==3:# vat *temp &temp array_element
          if line[-1][0]>='0' and line[-1][0]<='9':
            self.mips_writer.li(dst,constant)
          else:
            self.mips_writer.move(dst, src1)
        if len(line)==4:
          if line[2]=='CALL':
            temp_str = line[3].split('(')
            function_name = temp_str[0]
            params = temp_str[1][:-1].split(',')
            self.function_call(function_name, params)
            self.mips_writer.addi(dst, 'v0')
          # else :
          #   if line[3]=='+':
          #     if line[-1][0]>='0' and line[-1][0]<='9':
          #       return '\taddi %s,$zero,%s'%(self.regs.get_normal_reg(line[0],self.line_no),line[-1])
          #       self.mips_writer.addi()
          #     else:
          #       return '\tadd %s,$zero,%s'%(self.regs.get_normal_reg(line[0],self.line_no),self.regs.get_normal_reg(line[-1],self.line_no))
          #   if line[3]=='-':
          #     if line[-1][0]>='0' and line[-1][0]<='9':
          #       return '\taddi %s,$zero,-%s'%(self.regs.get_normal_reg(line[0],self.line_no),line[-1])
          #     else:
          #       return '\tadd %s,$zero,-%s'%(self.regs.get_normal_reg(line[0],self.line_no),self.regs.get_normal_reg(line[-1],self.line_no))
          #   if line[3]=='~': #mips实现按位取反 没写出来
          #     if line[-1][0]>='0' and line[-1][0]<='9':
          #       return '\taddi %s,$zero,%s'%(self.regs.get_normal_reg(line[0],self.line_no),line[-1])
          #   if line[3]=='!': #mips实现非
          #     if line[-1][0]>='0' and line[-1][0]<='9':
          #       return '\tor %s,$zero,%s'%(self.regs.get_normal_reg(line[0],self.line_no),line[-1])
          #     else:
          #       return '\tor %s,$zero,%s'%(self.regs.get_normal_reg(line[0],self.line_no),self.regs.get_normal_reg(line[-1],self.line_no))

        if len(line)==5: #目前不能解决的操作 >= <= ==  mul立即数等 因为需要临时变量寄存器
          if line[3]=='+':
            if line[-1][0]>='0' and line[-1][0]<='9':
              self.mips_writer.addi(dst,src1,constant)
            else:
              self.mips_writer.add(dst,src1,src2)
          if line[3]=='-':
            if line[-1][0]>='0' and line[-1][0]<='9':
              self.mips_writer.addi(dst,src1, '-'+(constant))
            else:
              self.mips_writer.sub(dst,src1,src2)
          if line[3]=='*':
            self.mips_writer.mul(dst,src1,src2)
          if line[3]=='/':
            self.mips_writer.div(dst,src1,src2)
          if line[3]=='^':
            if line[-1][0]>='0' and line[-1][0]<='9':
              self.mips_writer.xori(dst,src1,constant)
            else:
              self.mips_writer.xor(dst,src1,src2)
          if line[3]=='<':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.slti(dst,src1,constant)
            else:
              self.mips_writer.slt(dst,src1,src2)
          if line[3]=='>':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.gti(dst,src1,constant)
            else:
              self.mips_writer.gt(dst,src1,src2)
          if line[3]=='<=':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.lei(dst,src1,constant)
            else:
              self.mips_writer.le(dst,src1,src2)
          if line[3]=='>=':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.gei(dst,src1,constant)
            else:
              self.mips_writer.ge(dst,src1,src2)
          if line[3]=='&&':
            self.mips_writer.and_(dst,src1,src2)

          if line[3]=='||':
              self.mips_writer.or_(dst,src1,src2)

          if line[3]=='&':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.andi(dst,src1,constant)
            else:
              self.mips_writer.and_(dst,src1,src2)
          if line[3]=='|':
            if line[-1][0] >= '0' and line[-1][0] <= '9':
              self.mips_writer.ori(dst, src1, constant)
            else:
              self.mips_writer.or_(dst,src1,src2)
          if line[3]=='<<':
            if line[-1][0]>='0' and line[-1][0]<='9':
              self.mips_writer.sll(dst,src1,constant)
            else:
              self.mips_writer.sllv(dst,src1,src2)
          if line[3]=='>>':
            if line[-1][0]>='0' and line[-1][0]<='9':
              self.mips_writer.srl(dst,src1,constant)
            else:
              self.mips_writer.srlv(dst,src1,src2)
      if line[0]=='GOTO': #GOTO label1
        self.mips_writer.j(line[1])
      if line[0]=='IF': #IF var GOTO label1
        self.mips_writer.bne(self.regs.get_normal_reg(line[1],self.line_no),line[-1])
      if line[0]=='IFNOT': #IFNOT var GOTO label1
        self.mips_writer.beq(self.regs.get_normal_reg(line[1],self.line_no),line[-1])
      if line[0]=='RETURN': #RETURN var1
        #return '\tmove $v0,%s\n\tjr $ra'%self.regs.get_normal_reg(line[1],self.line_no)
        self.function_return(line[1] if len(line)>1 else None)
      # if line[0]=='MALLOC': #MALLOC var1[size]
      #   s = line[1].split('[')
      #   offset = stack_frames[-1].request_space(s[1][:-1])
      #   self.mips_writer.addi(s[0], 'sp', -offset)
      if line[0]=='CALL': #CALL f (var1,var2,var3...) 这里不太确定
        temp_str = line[3].split('(')
        function_name = temp_str[0]
        params = temp_str[1][:-1].split(',')
        # if function_name=='read' or function_name=='print':
        #   # TODO 这个不知道能不能用，我暂时先不改了 -awmleer
        #   self.mips_writer.addi('sp', 'sp', -4)
        #   self.mips_writer.sw('ra', 'sp')
        #
        #   return '\taddi $sp,$sp,-4\n\tsw $ra,0($sp)\n\tjal %s\n\tlw $ra,0($sp)\n\tmove %s,$v0\n\taddi $sp,$sp,4'%(line[-1],self.regs.get_normal_reg(line[0],self.line_no))
        # else:
        self.function_call(function_name, params)
      if line[0]=='Function': #FUNCTION f(var1,var2,var3...):
        temp_str = line[1].split('(')
        function_name=temp_str[0]
        params = temp_str[1][:-2].split(',')
        self.mips_writer.write_function_label(function_name)
        count = 0
        for param in params:
          self.mips_writer.addi(self.regs.get_normal_reg(param, self.line_no), 'a'+str(count))
          count += 1
      self.line_no=self.line_no+1

    # return '\tbeq %s,%s,%s' % (
    # self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line[-1])
    # if line[2] == '!=':
    #   return '\tbne %s,%s,%s' % (
    #   self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line[-1])
    # if line[2] == '>':
    #   return '\tbgt %s,%s,%s' % (
    #   self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line[-1])
    # if line[2] == '<':
    #   return '\tblt %s,%s,%s' % (
    #   self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line[-1])
    # if line[2] == '>=':
    #   return '\tbge %s,%s,%s' % (
    #   self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line[-1])
    # if line[2] == '<=':
    #   return '\tble %s,%s,%s' % (
    #   self.regs.get_normal_reg(line[1],self.line_no), self.regs.get_normal_reg(line[3],self.line_no), line

#parser() #主函数


# #处理变量
# def varDistribution(Inter):
#   global variables
#   temp_re='(temp\d+)'
#   for line in Inter:
#     temps=re.findall(temp_re,' '.join(line))
#     variables.append(temps)
#
# #记录所有变量 读取所有的中间代码 然后把换行的分开进不同点line

#
# #取得变量的寄存器
# def self.regs.get_normal_reg(string):
#   try:
#     variables.remove(string)
#   except:
#     pass
#   if string in table:
#     return '$'+table[string]  #如果已经存在寄存器分配，那么直接返回寄存器
#   else:
#     keys=[]
#     for key in table:         #已经分配寄存器的变量key
#       keys.append(key)
#     for key in keys:          #当遇到未分配寄存器的变量时，清空之前所有分配的临时变量的映射关系！！！
#       if 'temp' in  key and key not in variables: #
#         reg_ok[table[key]]=1
#         del table[key]
#     for reg in regs:          #对于所有寄存器
#       if reg_ok[reg]==1:    #如果寄存器可用
#         table[string]=reg #将可用寄存器分配给该变量，映射关系存到table中
#         reg_ok[reg]=0     #寄存器reg设置为已用
#         return '$'+reg

