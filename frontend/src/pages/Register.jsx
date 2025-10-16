// src/pages/Register.jsx
import React from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useMutation } from "@tanstack/react-query";
import { registerUser } from "../api/auth";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import clsx from "clsx";
import useAuth from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

toast.configure && toast.configure();

const schema = yup.object({
  first_name: yup.string().required("First name is required"),
  last_name: yup.string().required("Last name is required"),
  email: yup.string().email("Invalid email").required("Email is required"),
  password: yup.string().min(8, "Minimum 8 characters").required("Password is required"),
  password_confirm: yup
    .string()
    .oneOf([yup.ref("password"), null], "Passwords must match")
    .required("Please confirm password"),
  // Add more fields if your serializer expects them (username, phone, bio, etc)
});

export default function Register() {
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError: setFieldError,
  } = useForm({
    resolver: yupResolver(schema),
  });

  const mutation = useMutation({
    mutationFn: async (payload) => {
      return await registerUser(payload);
    },
    onSuccess: (data) => {
      // Data structure depends on your backend.
      // Common patterns:
      // - returns user object + tokens -> { user: {...}, access: 'jwt', refresh: '...' }
      // - returns user only -> { id:..., email:... }
      toast.success("Registration successful");
      // if tokens provided, store them
      if (data?.access || data?.token || data?.access_token) {
        const token = data.access || data.token || data.access_token;
        localStorage.setItem("access_token", token);
      }
      if (data?.user) {
        setUser(data.user);
      } else {
        // optionally set minimal user representation
        setUser({ email: data.email || null });
      }
      // redirect to dashboard or login
      navigate("/dashboard", { replace: true });
    },
    onError: (err) => {
      // err is structured by api interceptor: {status, data, message}
      if (err?.data && typeof err.data === "object") {
        // Map field errors from DRF: { email: ["error"], non_field_errors: ["error"] }
        Object.entries(err.data).forEach(([key, val]) => {
          if (Array.isArray(val)) {
            // if key corresponds to form field, set field error
            if (["first_name", "last_name", "email", "password", "password_confirm", "username", "phone", "bio"].includes(key)) {
              setFieldError(key, { type: "server", message: val.join(" ") });
            } else if (key === "non_field_errors" || key === "detail") {
              toast.error(val.join(" "));
            } else {
              // unknown field -> show toast
              toast.error(`${key}: ${val.join(" ")}`);
            }
          } else if (typeof val === "string") {
            toast.error(val);
          }
        });
      } else {
        toast.error(err?.message || "Registration failed");
      }
    },
  });

  const onSubmit = (formData) => {
    // Prepare payload to send to backend; remove password_confirm
    const payload = {
      ...formData,
    };

    mutation.mutate(payload);
  };

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-900/60 backdrop-blur-sm border border-gray-800 p-8 rounded-xl shadow-lg">
        <h2 className="text-2xl font-semibold mb-4 text-white">Create an account</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1">First name</label>
              <input
                {...register("first_name")}
                className={clsx(
                  "w-full p-2 rounded bg-gray-800 border",
                  errors.first_name ? "border-red-500" : "border-gray-700"
                )}
                placeholder="First name"
              />
              <p className="text-xs text-red-400 mt-1">{errors.first_name?.message}</p>
            </div>

            <div>
              <label className="block text-sm mb-1">Last name</label>
              <input
                {...register("last_name")}
                className={clsx(
                  "w-full p-2 rounded bg-gray-800 border",
                  errors.last_name ? "border-red-500" : "border-gray-700"
                )}
                placeholder="Last name"
              />
              <p className="text-xs text-red-400 mt-1">{errors.last_name?.message}</p>
            </div>
          </div>

          <div>
            <label className="block text-sm mb-1">Username</label>
            <input
              {...register("username")}
              className={clsx("w-full p-2 rounded bg-gray-800 border", errors.username ? "border-red-500" : "border-gray-700")}
              placeholder="example"
            />
            <p className="text-xs text-red-400 mt-1">{errors.username?.message}</p>
          </div>

          <div>
            <label className="block text-sm mb-1">Email</label>
            <input
              {...register("email")}
              type="email"
              className={clsx("w-full p-2 rounded bg-gray-800 border", errors.email ? "border-red-500" : "border-gray-700")}
              placeholder="you@example.com"
            />
            <p className="text-xs text-red-400 mt-1">{errors.email?.message}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1">Password</label>
              <input
                {...register("password")}
                type="password"
                className={clsx("w-full p-2 rounded bg-gray-800 border", errors.password ? "border-red-500" : "border-gray-700")}
                placeholder="At least 8 characters"
                autoComplete="new-password"
              />
              <p className="text-xs text-red-400 mt-1">{errors.password?.message}</p>
            </div>

            <div>
              <label className="block text-sm mb-1">Confirm password</label>
              <input
                {...register("password_confirm")}
                type="password"
                className={clsx("w-full p-2 rounded bg-gray-800 border", errors.password_confirm ? "border-red-500" : "border-gray-700")}
                placeholder="Confirm password"
                autoComplete="new-password"
              />
              <p className="text-xs text-red-400 mt-1">{errors.password_confirm?.message}</p>
            </div>
          </div>

          {/* Optional fields example (uncomment if needed) */}
          {/* <div>
            <label className="block text-sm mb-1">Phone</label>
            <input {...register("phone")} className="w-full p-2 rounded bg-gray-800 border border-gray-700" placeholder="+91..." />
          </div> */}

          <button
            type="submit"
            className="w-full py-2 rounded bg-blue-600 hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={mutation.isLoading}
          >
            {mutation.isLoading ? "Creating account..." : "Create account"}
          </button>

          <div className="text-sm text-gray-400 mt-2">
            Already have an account?{" "}
            <a href="/login" className="text-blue-400 hover:underline">
              Log in
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}
