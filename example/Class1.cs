using System.Text;
using System.Runtime.InteropServices;
using System;

namespace example
{
    public class Class1
    {
    	public static int Test(IntPtr arg, int size) {
            var buf = new byte[size];
            Marshal.Copy(arg, buf);
            var bufAsString = Encoding.UTF8.GetString(buf);
            var result = bufAsString.Length;
            Console.WriteLine($"Called {nameof(Test)} in {nameof(Class1)} with {bufAsString}, returning {result}");
            return result;
        }
    }
}
