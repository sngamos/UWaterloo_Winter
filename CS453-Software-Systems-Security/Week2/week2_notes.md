# Week 2 notes

## Hearbleed Vulnerability (CVE-2014-0610)

![alt text](diagrams/heartbleed.png)
Keep sending heartbeat messages to server to maintain connection.  
Server doesn't verify the no. bytes of the echo message, and sends that overflow from that of the requested echo string.  

## demo buffer overflow

```
#include <stdio.h>
#include <unistd.h>

int vuln(){
    char buf(80);
    int r;
    r = read(0,buf,400)
    printf("\nRead %d bytes\n",r);
    return 0;
}
int main(int argc, char *argv[]){
    printf("Try to exec /bin/ls");
    vuln();
    return 0;
}
```

**Shellcode concept**  
Code can be data and Data can be code in shellcode.  
Can store data in shellcode buffer and then execute it later.

**Concept: Exploiting the code above**  
Buffer overflow exploit:  

buffer is 80 bytes long but r reads 400 bytes.  
To exploit this vulnerable code,  
overflow the buffer, then change the return address to something that you control (some function), then the function will be executed, allowing you to RCE.

**Exploiting the code method**  
1. generate needle file with 256 bytes.
2. in gdb, run the code file and use the needle file as input.
3. observe that the stack pointer ends at 67th byte
4. at the 68th byte is when the return address is stored.
5. find the return address of the buf to using gdb.
6. overwrite the return address at the 68th byte w the address of the start of the buf.
7. run the code and it will run the "ls" command.


## demo Use after free

continue at slide 15-20

## Memory safety

Types of memory corruption:
1. memory errors
2. violations of memory safety properties
3. unsafe programs

A program is memory safe if it is free of memory errors.  

How is memory safety ensured?

Observation 1: At **runtime**, memory is a pool of objects, can be stack or heap, etc.

Observation 2: Each object has known and limited **size** and **lifetime**.  
e.g 
- size: malloc() used to allocate size for a object.  
- lifetime: object become "alive" when malloc() called, object "killed" when free() called.

Observation 3: Once allocated, size of object **never** changes

Observation 4: memory access is always object-oriented.
- Memory read: (object_id,offeset,length)
    - e.g (0xF0C,2,5) = I want to read the object 0xF0C 2 bytes after the start, then read the length of 5 bytes after the offset, i.e **3<sup>rd</sup>-7<sup>th</sup> byte**.

- Memory write: (object_id, offset, length, value)
    - e.g (0xF0C,2,5,12345) = I want to write to the object 0xF0C 2 bytes after the start, with a value "12345", with length of 5 from the **3<sup>rd</sup> - 7<sup>th</sup> byte**.
 
**Spatial safety**  
During the program execution, we have full knowledge of any object in memory of its properties: **(object_id, size [int], alive [bool])**  

For any memory access we also know:
-  Memory Read: (object_id, offset[int],length[int])
- Memory Write: (object_id, offset[int],length[int], _)

Spatial safety is violated if:  
1. Overflow: offset + length >= size of object
2. Underflow: offset < 0 

**Examples**  
```
int foo(int x) {
int arr[16] = {0};
return arr[x];
}
```
Violation:  
Attacker can input x with value x<0 or x>=16, which will underflow or overflow the buffer.

```
long foo() {
int a = 0;
return *(long *)(&a);
}
```
Violation:  
1. int data type is 4 bytes, size of a is 4 bytes.
2. `&a` gets the address of `a` (4 bytes).
3. (long *)(&a) **typecasts** the `int*` of `a` to a `long*`, where `long` is 8 bytes.
4. *(long *)(&a) **dereferences** this `long*`, which means 8 bytes is read from `a`'s address.
5. out of bounds memory access.

```
int foo(int *p) {
// it is possible that p == NULL
return *p + 42;
}
```

**Violation**  
1. `foo()` takes in a pointer object `p`.
2. `*p` dereferences `p`, assuming `p` points to a valid memory address. i.e read from address at pointer `p`.
3. if `p == NULL` then dereferencing a NULL pointer with `*p` results in memory access at address `0x0`, which is invalid.
4. out of bounds memory access, or segmentation fault.

NULL-pointer dereferencing is sometimes considered **undefined behaviour**, i.e this behaviour is not given in the C language specification, most OS will panic the program when such behaviour is detected.

Since we know that for any object in the memory, (object_id != 0, size [int], alive [bool]), if `object_id == 0`, it is a NULL-pointer dereference.

## Temportal safety

read slide 28 - 33

## Exploit mitigation

Given a set of bugs, prevent them.  
Mitigation does **NOT** include detecting the bug

### Methods of mitigation
1. Principle of least privileges. (PoLP)
2. Reference Monitoring / program shepherding
3. Moving-target defense

#### Principle of least privileges  
**Data Execution Prevention - DEP**  
a.k.a  
**W⊕X** -  Write exclusive or Execute.

Both mean: You can only **write** or **execute** code in a memory region one at a time, not both together.

Continue from slide 7