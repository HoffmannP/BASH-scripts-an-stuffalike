wordlist = 'Ta,Sche,re,isch,scho,usch,sch,schli,ten,schla,fen,schne,fi,mi,schen,Scha,fe,le,scher,Schu,le,zisch,schi,ben'.split(',')
randomWord = () => wordlist[Math.floor(Math.random() * wordlist.length)]
list = Array(20).fill(0).map(i => `${randomWord()} - ${randomWord()}`)
console.log(list.join('\n'))
