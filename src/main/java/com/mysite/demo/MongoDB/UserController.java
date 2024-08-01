package com.mysite.demo.MongoDB;

import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.annotation.OptBoolean;
import com.mysite.demo.MongoDB.DataSchema.StaticInfo;
import com.mysite.demo.MongoDB.DataSchema.DentCodeData;
import com.mysite.demo.MongoDB.DataSchema.DynamicInfoData;

import org.bson.Document;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.List;
import java.util.Optional;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/info/name={id}")
    public Optional<DentCodeData> getInfoDataById (@PathVariable String id) {
        return userService.getFindHospitalCode(id);
    }

    @GetMapping("/info/all")
    public List<DentCodeData> getDiskDataById (@PathVariable String id) {
        return userService.getAllInfoData();
    }
}
