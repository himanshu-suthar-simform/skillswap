import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useMutation } from "@tanstack/react-query";
import { loginUser } from "../api/auth";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import clsx from "clsx";
import { useNavigate, Link } from "react-router-dom";
import useAuth from "../hooks/useAuth";

toast.configure && toast.configure();

const schema = yup.object({
  email: yup.string().email("Invalid email").required("Email is required"),
  password: yup.string().required("Password is required"),
});

export default function Login() {
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: yupResolver(schema),
  });

  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      if (data.access) {
        localStorage.setItem("access_token", data.access);
      }
      if (data.refresh) {
        localStorage.setItem("refresh_token", data.refresh);
      }

      toast.success("Login successful!");

      // (Optional) Decode token to extract user info if backend doesn't send user details
      setUser({ email: data?.user?.email }); // update if you decode token

      navigate("/dashboard", { replace: true });
    },
    onError: (err) => {
      if (err?.data) {
        const errorMsg =
          err.data?.detail ||
          err.data?.non_field_errors?.join(" ") ||
          "Invalid email or password";

        toast.error(errorMsg);
      } else {
        toast.error("Login failed. Please try again.");
      }
    },
  });

  const onSubmit = (formData) => {
    mutation.mutate(formData);
  };

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900/60 backdrop-blur-sm border border-gray-800 p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl font-semibold mb-4 text-white">Log in to your account</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div>
            <label className="block text-sm mb-1">Email</label>
            <input
              {...register("email")}
              type="email"
              className={clsx(
                "w-full p-2 rounded bg-gray-800 border",
                errors.email ? "border-red-500" : "border-gray-700"
              )}
              placeholder="you@example.com"
            />
            <p className="text-xs text-red-400 mt-1">{errors.email?.message}</p>
          </div>

          <div>
            <label className="block text-sm mb-1">Password</label>
            <input
              {...register("password")}
              type="password"
              className={clsx(
                "w-full p-2 rounded bg-gray-800 border",
                errors.password ? "border-red-500" : "border-gray-700"
              )}
              placeholder="Enter your password"
            />
            <p className="text-xs text-red-400 mt-1">{errors.password?.message}</p>
          </div>

          <button
            type="submit"
            className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={mutation.isLoading}
          >
            {mutation.isLoading ? "Logging in..." : "Log in"}
          </button>

          <div className="text-sm text-gray-400 mt-2">
            Don’t have an account?{" "}
            <Link to="/register" className="text-blue-400 hover:underline">
              Register
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
