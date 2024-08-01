package com.mysite.demo;

import java.util.List;
import java.util.ArrayList;
import java.util.Optional;

import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import com.mysite.demo.MongoDB.DataSchema.DentCodeData;
import com.mysite.demo.MongoDB.DataSchema.StaticInfo;
import com.mysite.demo.MongoDB.DataSchema.DynamicInfoData;
import com.mysite.demo.MongoDB.DataSchema.TimeData;

import com.mysite.demo.MongoDB.Repository.DynamicInfoRepository;
import com.mysite.demo.MongoDB.Repository.StaticInfoRepository;

import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import lombok.Setter;


@RequiredArgsConstructor
@Controller
public class ProjectController {

    private final DynamicInfoRepository diskRepository;
    private final StaticInfoRepository infoRepository;

    @GetMapping("/")
    public String root() {
        return "redirect:/Hello";
    }

    @GetMapping("/Hello")
    public String greet() {
        return "Hello Test";
    }
}
