using System.Text;
using System.Runtime.InteropServices;
using System;

namespace Example
{
    public class TestClass
    {
    	public static int Test(IntPtr arg, int size) {
            var buf = new byte[size];
            Marshal.Copy(arg, buf, 0, size);
            var bufAsString = Encoding.UTF8.GetString(buf);
            var result = bufAsString.Length;
            Console.WriteLine($"Called {nameof(Test)} in {nameof(TestClass)} with {bufAsString}, returning {result}");
            Console.WriteLine($"Binary data: {Convert.ToBase64String(buf)}");

            return result;
        }
    }
}
